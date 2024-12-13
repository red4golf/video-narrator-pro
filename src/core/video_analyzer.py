"""
Video analysis module for Video Narrator Pro.
Handles video processing, frame extraction, and GPT-4 Vision analysis.
"""

import os
from pathlib import Path
import logging
import time
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import json

from moviepy.editor import VideoFileClip
from PIL import Image
from openai import OpenAI

from ..utils.progress_tracking import ProgressTracker
from ..utils.file_handling import FileHandler
from .templates import Template

class VideoAnalyzer:
    """Handles video processing and frame analysis"""
    
    def __init__(
        self, 
        video_path: str, 
        template: Template,
        openai_client: OpenAI,
        progress_tracker: Optional[ProgressTracker] = None,
        output_dir: Optional[str] = None,
        frame_interval: int = 1
    ):
        """Initialize video analyzer"""
        self.video_path = Path(video_path)
        self.template = template
        self.client = openai_client
        self.progress = progress_tracker
        self.frame_interval = frame_interval
        
        # Setup output directories
        self.base_name = FileHandler.get_base_name(video_path)
        if output_dir:
            self.output_dir = FileHandler.setup_output_directory(
                self.base_name,
                parent_dir=output_dir
            )
        else:
            self.output_dir = FileHandler.setup_output_directory(self.base_name)
            
        self.frames_dir = self.output_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        # Initialize results storage
        self.frame_data: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def update_progress(self, message: str) -> None:
        """Update progress tracker"""
        if self.progress:
            self.progress.update(message)
        logging.info(message)

    def extract_frames(self) -> bool:
        """Extract frames from video at specified interval"""
        try:
            self.update_progress("Loading video...")
            with VideoFileClip(str(self.video_path)) as video:
                # Store video metadata
                self.metadata = {
                    'duration': video.duration,
                    'fps': video.fps,
                    'size': video.size,
                    'filename': self.base_name
                }
                
                # Calculate frame times
                frame_times = range(0, int(video.duration), self.frame_interval)
                total_frames = len(frame_times)
                
                self.update_progress(f"Extracting {total_frames} frames...")
                for i, t in enumerate(frame_times, 1):
                    # Get and save frame
                    frame = video.get_frame(t)
                    frame_path = self.frames_dir / f"frame_{t:04d}.jpg"
                    
                    # Convert to PIL Image for processing
                    image = Image.fromarray(frame)
                    
                    # Resize if needed (GPT-4 Vision has size limits)
                    max_size = (2000, 2000)  # Adjust based on API requirements
                    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save frame
                    image.save(frame_path, quality=95)
                    
                    # Store frame information
                    self.frame_data.append({
                        'timestamp': t,
                        'frame_path': str(frame_path),
                        'index': i,
                        'total_frames': total_frames
                    })
                    
                    self.update_progress(f"Extracted frame {i} of {total_frames}")
                
                return True
                
        except Exception as e:
            logging.error(f"Error extracting frames: {str(e)}")
            raise

    def analyze_frame(self, frame_info: Dict[str, Any]) -> str:
        """Analyze a single frame using GPT-4 Vision"""
        try:
            # Update progress
            self.update_progress(
                f"Analyzing frame {frame_info['index']} of {frame_info['total_frames']}"
            )
            
            # Read and encode image
            with open(frame_info['frame_path'], "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Create API request
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": self.template.analysis_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=300
            )
            
            # Add delay to avoid rate limits
            time.sleep(0.5)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error analyzing frame: {str(e)}")
            raise

    def analyze_video(self) -> str:
        """Process and analyze the video"""
        try:
            # Extract frames
            if not self.extract_frames():
                raise Exception("Frame extraction failed")
            
            # Analyze frames
            self.update_progress("Starting frame analysis...")
            analysis_results = []
            
            for frame in self.frame_data:
                # Analyze frame
                description = self.analyze_frame(frame)
                
                # Store results
                analysis_results.append({
                    'timestamp': frame['timestamp'],
                    'frame_path': frame['frame_path'],
                    'narration': description
                })
            
            # Save analysis results
            self.update_progress("Saving analysis results...")
            results = {
                'video_name': self.base_name,
                'template_used': {
                    'id': self.template.id,
                    'name': self.template.name,
                    'is_customized': self.template.is_customized()
                },
                'metadata': self.metadata,
                'frames': analysis_results,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Save to JSON file
            output_path = self.output_dir / f"{self.base_name}_analysis.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Error in video analysis: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Clean up temporary files"""
        try:
            if self.frames_dir.exists():
                for frame_file in self.frames_dir.glob("*.jpg"):
                    try:
                        frame_file.unlink()
                    except Exception as e:
                        logging.warning(f"Error deleting frame {frame_file}: {e}")
                self.frames_dir.rmdir()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def __enter__(self) -> 'VideoAnalyzer':
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        if exc_type is not None:
            logging.error(f"Error during video analysis: {str(exc_val)}")
        self.cleanup()