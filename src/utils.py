import os
from pathlib import Path
import logging
import base64
from datetime import datetime
from tkinter import ttk

class ProgressTracker:
    """Handles progress updates in the GUI"""
    def __init__(self, progress_bar, progress_label):
        self.progress_bar = progress_bar
        self.progress_label = progress_label

    def update(self, message):
        """Update progress message and ensure GUI updates"""
        if self.progress_label:
            self.progress_label.config(text=message)
            self.progress_label.update()

    def start(self):
        """Start progress bar animation"""
        if self.progress_bar:
            self.progress_bar.start()

    def stop(self):
        """Stop progress bar animation"""
        if self.progress_bar:
            self.progress_bar.stop()

class FileHandler:
    """Handles file operations and path management"""
    @staticmethod
    def setup_output_directory(base_name, parent_dir=None):
        """Create and return output directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if parent_dir:
            output_dir = Path(parent_dir) / f"{base_name}_{timestamp}"
        else:
            output_dir = Path(f"{base_name}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    def get_base_name(file_path):
        """Extract base name from file path without extension"""
        return Path(file_path).stem

    @staticmethod
    def ensure_directory(directory):
        """Ensure directory exists, create if it doesn't"""
        Path(directory).mkdir(parents=True, exist_ok=True)

class TimeFormatter:
    """Handles time format conversions"""
    @staticmethod
    def seconds_to_timestamp(seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds) // 60
        remaining_seconds = int(seconds) % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    @staticmethod
    def frame_to_timecode(frame_number, fps=30):
        """Convert frame number to timecode"""
        seconds = frame_number / fps
        return TimeFormatter.seconds_to_timestamp(seconds)

class ImageHandler:
    """Handles image processing operations"""
    @staticmethod
    def image_to_base64(image_path):
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f"Error converting image to base64: {str(e)}")
            raise

class Logger:
    """Handles application logging"""
    @staticmethod
    def setup(output_dir, name='video_narrator'):
        """Setup logging configuration"""
        log_file = Path(output_dir) / f"{name}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(name)

def create_styled_frame(parent, padding="10", **kwargs):
    """Create a styled ttk Frame"""
    frame = ttk.Frame(parent, padding=padding, **kwargs)
    return frame

def create_styled_button(parent, text, command, **kwargs):
    """Create a styled ttk Button"""
    button = ttk.Button(parent, text=text, command=command, **kwargs)
    return button

def create_styled_label(parent, text, **kwargs):
    """Create a styled ttk Label"""
    label = ttk.Label(parent, text=text, **kwargs)
    return label