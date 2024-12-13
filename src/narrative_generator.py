import json
import logging
from pathlib import Path
import time
from .utils import TimeFormatter, FileHandler, ProgressTracker

class NarrativeGenerator:
    def __init__(self, json_path, template, openai_client, progress_tracker=None):
        """Initialize narrative generator with analysis results and template"""
        self.json_path = Path(json_path)
        self.template = template
        self.client = openai_client
        self.progress = progress_tracker
        
        # Read analysis results
        with open(json_path, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
            
        # Setup output directory
        self.base_name = self.analysis_data['video_name']
        self.output_dir = FileHandler.setup_output_directory(
            f"{self.base_name}_narration",
            parent_dir=self.json_path.parent
        )

    def update_progress(self, message):
        """Update progress in GUI if tracker exists"""
        if self.progress:
            self.progress.update(message)
        logging.info(message)

    def identify_scene_changes(self):
        """Group frames into coherent scenes"""
        scenes = []
        current_scene = []
        
        for frame in self.analysis_data['frames']:
            description = frame['narration'].lower()
            
            # Check for scene transition indicators
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

    def create_scene_narrative(self, scene):
        """Generate narrative for a single scene"""
        try:
            # Prepare scene context
            scene_start = TimeFormatter.seconds_to_timestamp(scene[0]['timestamp'])
            descriptions = [
                f"[{TimeFormatter.seconds_to_timestamp(frame['timestamp'])}] {frame['narration']}"
                for frame in scene
            ]
            
            scene_context = "\n".join(descriptions)
            
            # Get narrative from GPT
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.template.narration_prompt},
                    {"role": "user", "content": f"Create a flowing narrative for this scene starting at [{scene_start}]:\n\n{scene_context}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Add small delay to avoid rate limits
            time.sleep(0.5)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating scene narrative: {str(e)}")
            raise

    def generate_complete_narrative(self):
        """Generate complete narrative script"""
        try:
            self.update_progress("Identifying scene changes...")
            scenes = self.identify_scene_changes()
            
            self.update_progress("Generating narrative...")
            scene_narratives = []
            
            for i, scene in enumerate(scenes, 1):
                self.update_progress(f"Processing scene {i} of {len(scenes)}")
                narrative = self.create_scene_narrative(scene)
                scene_narratives.append(narrative)
            
            # Combine all narratives
            full_narrative = "\n\n".join(scene_narratives)
            
            # Final pass to ensure smooth transitions
            self.update_progress("Polishing final narrative...")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.template.narration_prompt},
                    {"role": "user", "content": "Polish this narrative, ensuring smooth transitions while maintaining timestamps:\n\n" + full_narrative}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating complete narrative: {str(e)}")
            raise

    def create_script_header(self):
        """Create professional script header"""
        duration = TimeFormatter.seconds_to_timestamp(self.analysis_data['metadata']['duration'])
        return f"""NARRATION SCRIPT
Title: {self.base_name}
Duration: {duration}
Template: {self.template.name}
Generated: {time.strftime('%B %d, %Y')}

Style Notes:
- Natural, conversational tone
- Clear transitions between scenes
- Professional but approachable
- Veteran narrator voice

=====================================================

"""

    def generate_script(self):
        """Generate and save complete narration script"""
        try:
            # Generate narrative
            narrative = self.generate_complete_narrative()
            
            # Combine with header
            script_content = self.create_script_header() + narrative
            
            # Save script
            self.update_progress("Saving script...")
            output_path = self.output_dir / f"{self.base_name}_narration.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Error generating script: {str(e)}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(f"Error during script generation: {str(exc_val)}")
        return False