"""
File handling utilities for the Video Narrator Pro application.
Manages file operations, paths, and directory structures.
"""

import os
from pathlib import Path
from datetime import datetime
import json
import logging
import shutil

class FileHandler:
    """Handles file operations and path management"""
    
    @staticmethod
    def setup_output_directory(base_name, parent_dir=None, include_timestamp=True):
        """
        Create and return output directory path.
        
        Args:
            base_name (str): Base name for the directory
            parent_dir (str, optional): Parent directory path. Defaults to None.
            include_timestamp (bool, optional): Include timestamp in directory name. Defaults to True.
            
        Returns:
            Path: Created directory path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        dir_name = f"{base_name}_{timestamp}" if timestamp else base_name
        
        if parent_dir:
            output_dir = Path(parent_dir) / dir_name
        else:
            output_dir = Path(dir_name)
            
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    def ensure_directory(directory):
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory (str or Path): Directory path
            
        Returns:
            Path: Directory path
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_base_name(file_path):
        """
        Extract base name from file path without extension.
        
        Args:
            file_path (str or Path): File path
            
        Returns:
            str: Base name without extension
        """
        return Path(file_path).stem

    @staticmethod
    def save_json(data, file_path, indent=2):
        """
        Save data to JSON file.
        
        Args:
            data (dict): Data to save
            file_path (str or Path): Output file path
            indent (int, optional): JSON indentation. Defaults to 2.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)

    @staticmethod
    def load_json(file_path):
        """
        Load data from JSON file.
        
        Args:
            file_path (str or Path): JSON file path
            
        Returns:
            dict: Loaded data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def safe_file_name(name):
        """
        Convert string to safe file name.
        
        Args:
            name (str): Original name
            
        Returns:
            str: Safe file name
        """
        # Replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        safe_name = ''.join(c if c not in unsafe_chars else '_' for c in name)
        return safe_name.strip()

    @staticmethod
    def get_unique_path(base_path):
        """
        Generate unique file path by appending number if needed.
        
        Args:
            base_path (str or Path): Original file path
            
        Returns:
            Path: Unique file path
        """
        path = Path(base_path)
        if not path.exists():
            return path
            
        counter = 1
        while True:
            new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    @staticmethod
    def cleanup_directory(directory, pattern=None, older_than=None):
        """
        Clean up files in directory based on pattern and age.
        
        Args:
            directory (str or Path): Directory to clean
            pattern (str, optional): File pattern to match. Defaults to None.
            older_than (datetime, optional): Delete files older than this. Defaults to None.
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                return

            for item in directory.glob(pattern or '*'):
                if older_than and item.stat().st_mtime >= older_than.timestamp():
                    continue
                    
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    logging.warning(f"Failed to delete {item}: {e}")
                    
        except Exception as e:
            logging.error(f"Error cleaning directory {directory}: {e}")

    @staticmethod
    def get_file_size(file_path):
        """
        Get human-readable file size.
        
        Args:
            file_path (str or Path): Path to file
            
        Returns:
            str: Human-readable file size
        """
        size = Path(file_path).stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"