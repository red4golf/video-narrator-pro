"""
Narrative generator module for Video Narrator Pro.
Creates natural narration scripts from video analysis results.
Outputs both clean narration text and technical timing information.
"""

import json
from pathlib import Path
import logging
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from openai import OpenAI

from ..utils.progress_tracking import ProgressTracker
from ..utils.file_handling import FileHandler
from .templates import Template

class NarrativeGenerator:
    """Generates natural narration from video analysis"""
    
    def __init__(
        self, 
        json_path: str,
        template: Template,
        openai_client: OpenAI,
        progress_tracker: Optional[ProgressTracker] = None,
        output_dir: Optional[str] = None
    ):
        """Initialize narrative generator"""
        self.json_path = Path(json_path)
        self.template = template
        self.client = openai_client
        self.progress = progress_tracker
        
        # Load analysis data
        with open(json_path, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
            
        # Setup output directory
        self.base_name = self.analysis_data['video_name']
        if output_dir:
            self.output_dir = FileHandler.setup_output_directory(
                f"{self.base_name}_narration",
                parent_dir=output_dir
            )
        else:
            self.output_dir = FileHandler.setup_output_directory(
                f"{self.base_name}_narration"
            )

    def update_progress(self, message: str) -> None:
        """Update progress tracker"""
        if self.progress:
            self.progress.update(message)
        logging.info(message)

    def identify_scenes(self) -> List[List[Dict[str, Any]]]:
        """Group frames into coherent scenes"""
        scenes = []
        current_scene = []
        
        for frame in self.analysis_data['frames']:
            description = frame['narration'].lower()
            
            # Check for scene transitions
            is_transition = any(term in description for term in [
                'moving to', 'entering', 'stepping into', 'next we have',
                'moving into', 'heading to', 'walking into', 'now in'
            ])
            
            if is_transition and current_scene:
                scenes.append(current_scene)
                current_scene = [frame]
            else:
                current_scene.append(frame)
                
        # Add final scene
        if current_scene:
            scenes.append(current_scene)
            
        return scenes

    def create_scene_narration(self, scene: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """Generate narration for a scene and return timing data"""
        try:
            # Prepare scene context for GPT
            scene_start = scene[0]['timestamp']
            descriptions = [frame['narration'] for frame in scene]
            
            scene_context = "\n".join(descriptions)
            
            # Get narrative from GPT
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": 
                     "Create flowing, natural narration suitable for text-to-speech. "
                     "Do not include timestamps, stage directions, or technical notes. "
                     f"Use the style specified:\n\n{self.template.narration_prompt}"},
                    {"role": "user", "content": 
                     f"Create natural narration from these descriptions:\n\n{scene_context}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            narration = response.choices[0].message.content
            
            # Create timing data
            timing_data = {
                'start_time': scene_start,
                'end_time': scene[-1]['timestamp'],
                'original_descriptions': descriptions
            }
            
            # Add small delay to avoid rate limits
            time.sleep(0.5)
            
            return narration.strip(), timing_data
            
        except Exception as e:
            logging.error(f"Error generating scene narration: {str(e)}")
            raise

    def create_complete_narration(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate complete narration and timing data"""
        try:
            self.update_progress("Identifying scenes...")
            scenes = self.identify_scenes()
            
            self.update_progress("Generating narration...")
            scene_narrations = []
            timing_data = []
            
            for i, scene in enumerate(scenes, 1):
                self.update_progress(f"Processing scene {i} of {len(scenes)}")
                narration, timing = self.create_scene_narration(scene)
                scene_narrations.append(narration)
                timing_data.append(timing)
            
            # Combine all narrations
            full_narration = "\n\n".join(scene_narrations)
            
            # Final polish for flow
            self.update_progress("Polishing final narration...")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": 
                     "Polish this narration for natural flow and text-to-speech delivery. "
                     "Ensure smooth transitions between paragraphs. "
                     "Do not include any technical notes or timing information."},
                    {"role": "user", "content": full_narration}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            polished_narration = response.choices[0].message.content.strip()
            
            return polished_narration, timing_data
            
        except Exception as e:
            logging.error(f"Error generating complete narration: {str(e)}")
            raise

    def save_timing_data(self, timing_data: List[Dict[str, Any]]) -> str:
        """Save technical timing information"""
        timing_info = {
            'video_name': self.base_name,
            'template_used': {
                'id': self.template.id,
                'name': self.template.name
            },
            'scene_timings': timing_data,
            'generated_at': datetime.now().isoformat()
        }
        
        output_path = self.output_dir / f"{self.base_name}_timing.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timing_info, f, indent=2)
            
        return str(output_path)

    def generate_script(self) -> Tuple[str, str]:
        """Generate and save narration files"""
        try:
            # Generate narration
            narration, timing_data = self.create_complete_narration()
            
            # Save clean narration for TTS
            self.update_progress("Saving narration files...")
            narration_path = self.output_dir / f"{self.base_name}_narration.txt"
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(narration)
            
            # Save timing data separately
            timing_path = self.save_timing_data(timing_data)
            
            return str(narration_path), timing_path
            
        except Exception as e:
            logging.error(f"Error generating script: {str(e)}")
            raise

    def __enter__(self) -> 'NarrativeGenerator':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(f"Error during script generation: {str(exc_val)}")