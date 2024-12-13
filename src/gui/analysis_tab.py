"""
Video analysis tab for Video Narrator Pro.
Manages video file selection and analysis process with template selection.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import Optional
import logging

from openai import OpenAI
from ..core.templates import TemplateManager, Template
from ..core.video_analyzer import VideoAnalyzer
from ..utils.progress_tracking import ProgressTracker
from .prompt_editor import PromptEditorDialog

class AnalysisTab(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Notebook,
        template_manager: TemplateManager,
        openai_client: OpenAI,
        progress_tracker: Optional[ProgressTracker] = None
    ):
        super().__init__(parent)
        
        # Store dependencies
        self.template_manager = template_manager
        self.client = openai_client
        self.progress = progress_tracker
        
        # Initialize state variables
        self.video_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.template_var = tk.StringVar()
        self.processing = False
        
        # Create interface
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template Selection
        template_frame = ttk.LabelFrame(main_frame, text="Template Selection", padding=5)
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Template dropdown and edit button
        template_row = ttk.Frame(template_frame)
        template_row.pack(fill=tk.X, pady=5)
        
        self.template_combo = ttk.Combobox(
            template_row,
            textvariable=self.template_var,
            values=self.template_manager.get_template_names(),
            state='readonly'
        )
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            template_row,
            text="Edit Template",
            command=self.edit_template
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Template description
        self.desc_label = ttk.Label(template_frame, wraplength=600)
        self.desc_label.pack(fill=tk.X, pady=5)
        
        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Video Selection", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Video file selection
        video_row = ttk.Frame(file_frame)
        video_row.pack(fill=tk.X, pady=5)
        
        ttk.Entry(
            video_row,
            textvariable=self.video_path_var,
            state='readonly'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            video_row,
            text="Select Video",
            command=self.select_video
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Output directory selection
        output_row = ttk.Frame(file_frame)
        output_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_row, text="Output:").pack(side=tk.LEFT)
        
        ttk.Entry(
            output_row,
            textvariable=self.output_dir_var,
            state='readonly'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(
            output_row,
            text="Select Folder",
            command=self.select_output
        ).pack(side=tk.LEFT)
        
        # Analysis Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.analyze_btn = ttk.Button(
            control_frame,
            text="Start Analysis",
            command=self.start_analysis,
            style="Accent.TButton"
        )
        self.analyze_btn.pack(side=tk.RIGHT)
        
        # Status display
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.template_combo.bind('<<ComboboxSelected>>', self.update_template_info)
        
    def select_video(self):
        """Handle video file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if file_path:
            self.video_path_var.set(file_path)
            # Set default output directory
            if not self.output_dir_var.get():
                self.output_dir_var.set(str(Path(file_path).parent))
                
    def select_output(self):
        """Handle output directory selection"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def edit_template(self):
        """Open template editor"""
        if not self.template_var.get():
            messagebox.showinfo("Template Required", "Please select a template first")
            return
            
        template = self.template_manager.get_template_by_name(self.template_var.get())
        if template:
            editor = PromptEditorDialog(self, template)
            if editor.show():
                self.update_template_info()
                
    def update_template_info(self, event=None):
        """Update template description display"""
        template = self.template_manager.get_template_by_name(self.template_var.get())
        if template:
            desc = template.description
            if template.is_customized():
                desc += "\n(Using custom prompts)"
            self.desc_label.config(text=desc)
            
    def update_status(self, message: str):
        """Update status display"""
        self.status_label.config(text=message)
        self.status_label.update()
        
    def start_analysis(self):
        """Begin video analysis process"""
        if self.processing:
            return
            
        # Validate inputs
        if not self.validate_inputs():
            return
            
        # Get template
        template = self.template_manager.get_template_by_name(self.template_var.get())
        
        # Update UI state
        self.processing = True
        self.analyze_btn.config(state=tk.DISABLED)
        self.clear_results()
        
        if self.progress:
            self.progress.show()
            
        # Start analysis thread
        self.analysis_thread = threading.Thread(
            target=self.run_analysis,
            args=(
                self.video_path_var.get(),
                template,
                self.output_dir_var.get()
            )
        )
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def validate_inputs(self) -> bool:
        """Validate all required inputs"""
        if not self.video_path_var.get():
            messagebox.showerror("Error", "Please select a video file")
            return False
            
        if not self.template_var.get():
            messagebox.showerror("Error", "Please select a template")
            return False
            
        if not self.output_dir_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return False
            
        return True
        
    def run_analysis(self, video_path: str, template: Template, output_dir: str):
        """Run analysis in separate thread"""
        try:
            with VideoAnalyzer(
                video_path,
                template,
                self.client,
                self.progress,
                output_dir
            ) as analyzer:
                result_path = analyzer.analyze_video()
                
            self.after(0, self.analysis_complete, result_path)
            
        except Exception as e:
            self.after(0, self.analysis_error, str(e))
            
    def analysis_complete(self, result_path: str):
        """Handle successful analysis completion"""
        self.processing = False
        self.analyze_btn.config(state=tk.NORMAL)
        
        if self.progress:
            self.progress.hide()
            
        self.add_result(f"Analysis complete!\n\nResults saved to:\n{result_path}")
        
    def analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.processing = False
        self.analyze_btn.config(state=tk.NORMAL)
        
        if self.progress:
            self.progress.hide()
            
        self.add_result(f"Error during analysis:\n{error_message}")
        messagebox.showerror("Analysis Error", error_message)
        
    def add_result(self, message: str):
        """Add message to results display"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, message)
        self.results_text.config(state=tk.DISABLED)
        
    def clear_results(self):
        """Clear results display"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
    def reset(self):
        """Reset tab to initial state"""
        self.video_path_var.set("")
        self.output_dir_var.set("")
        self.template_var.set("")
        self.clear_results()
        self.update_status("Ready")