"""
Narration generation tab for Video Narrator Pro.
Handles generation of clean narration scripts suitable for text-to-speech.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import Optional
import logging

from openai import OpenAI
from ..core.templates import TemplateManager, Template
from ..core.narrative_generator import NarrativeGenerator
from ..utils.progress_tracking import ProgressTracker
from .prompt_editor import PromptEditorDialog

class NarrationTab(ttk.Frame):
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
        self.analysis_path_var = tk.StringVar()
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
        template_frame = ttk.LabelFrame(main_frame, text="Narration Style", padding=5)
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
        file_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Analysis file selection
        analysis_row = ttk.Frame(file_frame)
        analysis_row.pack(fill=tk.X, pady=5)
        
        ttk.Entry(
            analysis_row,
            textvariable=self.analysis_path_var,
            state='readonly'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            analysis_row,
            text="Select Analysis",
            command=self.select_analysis
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
        
        # Generation Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.generate_btn = ttk.Button(
            control_frame,
            text="Generate Narration",
            command=self.start_generation,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.RIGHT)
        
        # Status display
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Preview Area
        preview_frame = ttk.LabelFrame(main_frame, text="Script Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect scrollbar
        self.preview_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.preview_text.yview)
        
        # Bind events
        self.template_combo.bind('<<ComboboxSelected>>', self.update_template_info)
        
    def select_analysis(self):
        """Handle analysis file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Analysis Results",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.analysis_path_var.set(file_path)
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
        
    def start_generation(self):
        """Begin narration generation process"""
        if self.processing:
            return
            
        # Validate inputs
        if not self.validate_inputs():
            return
            
        # Get template
        template = self.template_manager.get_template_by_name(self.template_var.get())
        
        # Update UI state
        self.processing = True
        self.generate_btn.config(state=tk.DISABLED)
        self.clear_preview()
        
        if self.progress:
            self.progress.show()
            
        # Start generation thread
        self.generation_thread = threading.Thread(
            target=self.run_generation,
            args=(
                self.analysis_path_var.get(),
                template,
                self.output_dir_var.get()
            )
        )
        self.generation_thread.daemon = True
        self.generation_thread.start()
        
    def validate_inputs(self) -> bool:
        """Validate all required inputs"""
        if not self.analysis_path_var.get():
            messagebox.showerror("Error", "Please select an analysis file")
            return False
            
        if not self.template_var.get():
            messagebox.showerror("Error", "Please select a template")
            return False
            
        if not self.output_dir_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return False
            
        return True
        
    def run_generation(self, analysis_path: str, template: Template, output_dir: str):
        """Run generation in separate thread"""
        try:
            with NarrativeGenerator(
                analysis_path,
                template,
                self.client,
                self.progress,
                output_dir
            ) as generator:
                narration_path, timing_path = generator.generate_script()
                
            self.after(0, self.generation_complete, narration_path, timing_path)
            
        except Exception as e:
            self.after(0, self.generation_error, str(e))
            
    def generation_complete(self, narration_path: str, timing_path: str):
        """Handle successful generation completion"""
        self.processing = False
        self.generate_btn.config(state=tk.NORMAL)
        
        if self.progress:
            self.progress.hide()
            
        # Show narration preview
        try:
            with open(narration_path, 'r', encoding='utf-8') as f:
                narration_text = f.read()
            self.set_preview(narration_text)
        except Exception as e:
            logging.error(f"Error loading preview: {e}")
            
        self.update_status("Generation complete!")
        messagebox.showinfo(
            "Generation Complete",
            f"Narration script saved to:\n{narration_path}\n\n"
            f"Timing data saved to:\n{timing_path}"
        )
        
    def generation_error(self, error_message: str):
        """Handle generation error"""
        self.processing = False
        self.generate_btn.config(state=tk.NORMAL)
        
        if self.progress:
            self.progress.hide()
            
        self.update_status("Error during generation")
        messagebox.showerror("Generation Error", error_message)
        
    def set_preview(self, text: str):
        """Update preview text"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.config(state=tk.DISABLED)
        
    def clear_preview(self):
        """Clear preview text"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
        
    def reset(self):
        """Reset tab to initial state"""
        self.analysis_path_var.set("")
        self.output_dir_var.set("")
        self.template_var.set("")
        self.clear_preview()
        self.update_status("Ready")