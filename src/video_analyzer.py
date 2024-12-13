from pathlib import Path
import json
import logging
from moviepy.editor import VideoFileClip
from PIL import Image
import time
from .utils import TimeFormatter, FileHandler, ImageHandler, ProgressTracker

class VideoAnalyzer:
    def __init__(self, video_path, template, openai_client, progress_tracker=None):
        """Initialize video analyzer with specified template and OpenAI client"""
        self.video_path = Path(video_path)
        self.template = template
        self.client = openai_client
        self.progress = progress_tracker
        
        # Setup output directory and logging
        self.base_name = FileHandler.get_base_name(video_path)
        self.output_dir = FileHandler.setup_output_directory(self.base_name)
        self.frames_dir = self.output_dir / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        # Analysis results
        self.frame_data = []

    def update_progress(self, message):
        """Update progress in GUI if tracker exists"""
        if self.progress:
            self.progress.update(message)
        logging.info(message)

    def extract_frames(self, interval=1.0):
        """Extract frames from video at specified interval"""
        try:
            self.update_progress("Loading video...")
            with VideoFileClip(str(self.video_path)) as video:
                duration = video.duration
                frame_times = range(0, int(duration), int(interval))
                total_frames = len(frame_times)

                self.update_progress(f"Extracting {total_frames} frames...")
                for i, t in enumerate(frame_times, 1):
                    # Get and save frame
                    frame = video.get_frame(t)
                    frame_path = self.frames_dir / f"frame_{t:04d}.jpg"
                    Image.fromarray(frame).save(frame_path)
                    
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

    def analyze_frame(self, frame_info):
        """Analyze a single frame using GPT-4 Vision"""
        try:
            # Convert image to base64
            base64_image = ImageHandler.image_to_base64(frame_info['frame_path'])
            
            # Update progress
            self.update_progress(
                f"Analyzing frame {frame_info['index']} of {frame_info['total_frames']}"
            )
            
            # Create GPT-4 Vision request
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
            
            # Add small delay to avoid rate limits
            time.sleep(0.5)
            
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Error analyzing frame: {str(e)}")
            raise

    def analyze_video(self):
        """Process and analyze the entire video"""
        try:
            # Extract frames
            if not self.extract_frames():
                raise Exception("Frame extraction failed")

            # Analyze each frame
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
                'template_used': self.template.id,
                'metadata': {
                    'duration': self.frame_data[-1]['timestamp'] + 1,
                    'frame_count': len(self.frame_data)
                },
                'frames': analysis_results
            }

            # Save to JSON file
            output_path = self.output_dir / f"{self.base_name}_analysis.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            return str(output_path)

        except Exception as e:
            logging.error(f"Error in video analysis: {str(e)}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(f"Error during video analysis: {str(exc_val)}")
        return False