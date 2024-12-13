import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

class PromptEditorDialog:
    def __init__(self, parent, template):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Prompts - {template.name}")
        self.dialog.geometry("800x600")
        self.template = template
        self.result = None
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Analysis prompt section
        ttk.Label(main_frame, text="Analysis Prompt", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.analysis_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.analysis_text.insert('1.0', self.template.analysis_prompt)

        # Narration prompt section
        ttk.Label(main_frame, text="Narration Prompt", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.narration_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.narration_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.narration_text.insert('1.0', self.template.narration_prompt)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Reset button (left-aligned)
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_prompts
        ).pack(side=tk.LEFT)

        # Save and Cancel buttons (right-aligned)
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Save Changes",
            command=self.save_changes
        ).pack(side=tk.RIGHT)

    def center_window(self):
        """Center the dialog window on the screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def reset_prompts(self):
        """Reset prompts to template defaults"""
        if messagebox.askyesno("Reset Prompts", "Reset both prompts to default values?"):
            self.template.reset_to_defaults()
            self.analysis_text.delete('1.0', tk.END)
            self.analysis_text.insert('1.0', self.template.analysis_prompt)
            self.narration_text.delete('1.0', tk.END)
            self.narration_text.insert('1.0', self.template.narration_prompt)

    def save_changes(self):
        """Save prompt changes and close dialog"""
        analysis_prompt = self.analysis_text.get('1.0', 'end-1c').strip()
        narration_prompt = self.narration_text.get('1.0', 'end-1c').strip()

        if not analysis_prompt or not narration_prompt:
            messagebox.showerror("Error", "Both prompts must have content")
            return

        self.template.analysis_prompt = analysis_prompt
        self.template.narration_prompt = narration_prompt
        self.result = True
        self.dialog.destroy()

    def show(self):
        """Show dialog and wait for it to close"""
        self.dialog.wait_window()
        return self.result