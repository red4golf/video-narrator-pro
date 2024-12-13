"""
Progress tracking utilities for the Video Narrator Pro application.
Handles progress bars, status updates, and progress reporting.
"""

import logging
from tkinter import ttk

class ProgressTracker:
    """Manages progress updates and status messages in the GUI"""
    
    def __init__(self, progress_bar=None, status_label=None):
        """
        Initialize progress tracker.
        
        Args:
            progress_bar (ttk.Progressbar): Progress bar widget
            status_label (ttk.Label): Status label widget
        """
        self.progress_bar = progress_bar
        self.status_label = status_label
        self._is_active = False

    @property
    def is_active(self):
        """Check if progress tracking is active"""
        return self._is_active

    def start(self):
        """Start progress tracking"""
        if self.progress_bar:
            self.progress_bar.start()
        self._is_active = True

    def stop(self):
        """Stop progress tracking"""
        if self.progress_bar:
            self.progress_bar.stop()
        self._is_active = False

    def update(self, message):
        """
        Update progress status message
        
        Args:
            message (str): Status message to display
        """
        if self.status_label:
            self.status_label.config(text=message)
            self.status_label.update()
        logging.info(message)

    def update_progress(self, value, maximum=100):
        """
        Update progress bar value
        
        Args:
            value (int): Current progress value
            maximum (int, optional): Maximum progress value. Defaults to 100.
        """
        if self.progress_bar and isinstance(self.progress_bar, ttk.Progressbar):
            self.progress_bar.configure(mode='determinate', maximum=maximum)
            self.progress_bar['value'] = value
            self.progress_bar.update()

    def set_indeterminate(self):
        """Set progress bar to indeterminate mode"""
        if self.progress_bar:
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start()

    def hide(self):
        """Hide progress tracking widgets"""
        self.stop()
        if self.progress_bar:
            self.progress_bar.pack_forget()
        if self.status_label:
            self.status_label.pack_forget()
        self._is_active = False

    def show(self):
        """Show progress tracking widgets"""
        if self.status_label:
            self.status_label.pack()
        if self.progress_bar:
            self.progress_bar.pack(fill='x', expand=True)
        self.start()
        self._is_active = True

class BatchProgressTracker(ProgressTracker):
    """Extended progress tracker for batch operations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_batch = 0
        self.total_batches = 0

    def start_batch(self, total_batches):
        """
        Start batch processing
        
        Args:
            total_batches (int): Total number of batches to process
        """
        self.total_batches = total_batches
        self.current_batch = 0
        self.start()

    def next_batch(self):
        """Move to next batch and update progress"""
        self.current_batch += 1
        if self.total_batches > 0:
            progress = (self.current_batch / self.total_batches) * 100
            self.update_progress(progress)
            self.update(f"Processing batch {self.current_batch} of {self.total_batches}")

    def complete(self):
        """Mark batch processing as complete"""
        self.update_progress(100)
        self.update("Processing complete")
        self.stop()