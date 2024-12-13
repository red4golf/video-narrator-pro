"""
Main window for Video Narrator Pro application.
Manages application initialization, layout, and tab coordination.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
from openai import OpenAI

from ..core.templates import TemplateManager
from ..utils.progress_tracking import ProgressTracker
from .analysis_tab import AnalysisTab
from .narration_tab import NarrationTab

class MainWindow:
    def __init__(self):
        self.setup_logging()
        self.initialize_app()
        self.create_gui()
        self.create_menu()
        self.create_status_bar()
        
    def setup_logging(self):
        """Initialize logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "app.log"),
                logging.StreamHandler()
            ]
        )
        
    def initialize_app(self):
        """Initialize application settings and dependencies"""
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            messagebox.showerror(
                "Configuration Error",
                "OpenAI API key not found. Please add it to your .env file."
            )
            raise SystemExit
            
        self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize template manager
        self.template_manager = TemplateManager()
        
    def create_gui(self):
        """Create main window and GUI elements"""
        # Create and configure root window
        self.root = tk.Tk()
        self.root.title("Video Narrator Pro")
        self.root.geometry("1024x768")
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_tabs()
        
    def setup_styles(self):
        """Configure ttk styles for consistent look"""
        style = ttk.Style()
        
        # General styles
        style.configure("TFrame", background="white")
        style.configure("TNotebook", background="white")
        style.configure("TLabel", background="white", padding=2)
        
        # Header styles
        style.configure(
            "Header.TLabel",
            font=("Helvetica", 16, "bold"),
            padding=5
        )
        
        # Custom button styles
        style.configure(
            "Action.TButton",
            font=("Helvetica", 10),
            padding=5
        )
        
        # Tab styles
        style.configure(
            "TNotebook.Tab",
            padding=[10, 5],
            font=("Helvetica", 10)
        )
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Templates menu
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Templates", menu=template_menu)
        template_menu.add_command(
            label="Manage Templates",
            command=self.manage_templates
        )
        template_menu.add_command(
            label="Reset to Defaults",
            command=self.reset_templates
        )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            padding=(5, 2)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            self.status_bar,
            mode='indeterminate',
            length=200
        )
        
    def create_tabs(self):
        """Create and initialize application tabs"""
        # Create shared progress tracker
        self.progress_tracker = ProgressTracker(
            self.progress_bar,
            self.status_label
        )
        
        # Analysis tab
        self.analysis_tab = AnalysisTab(
            self.notebook,
            self.template_manager,
            self.openai_client,
            self.progress_tracker
        )
        self.notebook.add(
            self.analysis_tab,
            text="Video Analysis"
        )
        
        # Narration tab
        self.narration_tab = NarrationTab(
            self.notebook,
            self.template_manager,
            self.openai_client,
            self.progress_tracker
        )
        self.notebook.add(
            self.narration_tab,
            text="Generate Narration"
        )
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def new_project(self):
        """Handle new project creation"""
        # Clear existing data
        self.analysis_tab.reset()
        self.narration_tab.reset()
        self.update_status("New project created")
        
    def open_project(self):
        """Handle project opening"""
        # TODO: Implement project loading
        pass
        
    def manage_templates(self):
        """Open template management dialog"""
        # TODO: Implement template management dialog
        pass
        
    def reset_templates(self):
        """Reset templates to defaults"""
        if messagebox.askyesno(
            "Reset Templates",
            "Reset all templates to default settings? Custom prompts will be lost."
        ):
            self.template_manager = TemplateManager()
            self.analysis_tab.refresh_templates()
            self.narration_tab.refresh_templates()
            self.update_status("Templates reset to defaults")
            
    def show_docs(self):
        """Show documentation"""
        # TODO: Implement documentation viewer
        pass
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Video Narrator Pro",
            "Video Narrator Pro\nVersion 1.0\n\n"
            "A professional tool for generating natural video narration scripts."
        )
        
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
def main():
    """Application entry point"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        messagebox.showerror(
            "Error",
            f"An error occurred starting the application:\n{str(e)}"
        )
        
if __name__ == "__main__":
    main()