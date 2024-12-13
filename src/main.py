[Previous code remains exactly the same until select_output_directory method...]

    def select_output_directory(self, mode):
        """Open directory dialog for output selection"""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if directory:
            if mode == 'analysis':
                self.analysis_output_var.set(directory)
            else:
                self.narration_output_var.set(directory)

    def show_progress(self, progress_bar, progress_label, progress_frame):
        """Show progress indicators"""
        progress_frame.pack(fill=tk.X, pady=10)
        progress_label.pack()
        progress_bar.pack(fill=tk.X)
        progress_bar.start()

    def hide_progress(self, progress_bar, progress_label, progress_frame):
        """Hide progress indicators"""
        progress_bar.stop()
        progress_frame.pack_forget()

    def start_analysis(self):
        """Start video analysis process"""
        if not self.video_path_var.get():
            messagebox.showerror("Error", "Please select a video file")
            return
            
        if not self.analysis_template_var.get():
            messagebox.showerror("Error", "Please select a template")
            return
            
        if not self.analysis_output_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        template = self.template_manager.get_template_by_name(
            self.analysis_template_var.get()
        )
        
        self.analyze_button.config(state='disabled')
        self.show_progress(
            self.analysis_progress,
            self.analysis_status,
            self.analysis_progress_frame
        )
        
        # Start analysis in separate thread
        thread = threading.Thread(
            target=self.run_analysis,
            args=(
                self.video_path_var.get(),
                template,
                self.analysis_output_var.get()
            )
        )
        thread.daemon = True
        thread.start()

    def run_analysis(self, video_path, template, output_dir):
        """Run video analysis in separate thread"""
        try:
            progress_tracker = ProgressTracker(
                self.analysis_progress,
                self.analysis_status
            )
            
            with VideoAnalyzer(
                video_path,
                template,
                self.client,
                progress_tracker,
                output_dir
            ) as analyzer:
                result_path = analyzer.analyze_video()
            
            self.root.after(0, self.analysis_complete, result_path)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def start_narration(self):
        """Start narration generation process"""
        if not self.json_path_var.get():
            messagebox.showerror("Error", "Please select an analysis file")
            return
            
        if not self.narration_template_var.get():
            messagebox.showerror("Error", "Please select a template")
            return
            
        if not self.narration_output_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        template = self.template_manager.get_template_by_name(
            self.narration_template_var.get()
        )
        
        self.generate_button.config(state='disabled')
        self.show_progress(
            self.narration_progress,
            self.narration_status,
            self.narration_progress_frame
        )
        
        # Start generation in separate thread
        thread = threading.Thread(
            target=self.run_narration,
            args=(
                self.json_path_var.get(),
                template,
                self.narration_output_var.get()
            )
        )
        thread.daemon = True
        thread.start()

    def run_narration(self, json_path, template, output_dir):
        """Run narration generation in separate thread"""
        try:
            progress_tracker = ProgressTracker(
                self.narration_progress,
                self.narration_status
            )
            
            with NarrativeGenerator(
                json_path,
                template,
                self.client,
                progress_tracker,
                output_dir
            ) as generator:
                result_path = generator.generate_script()
            
            self.root.after(0, self.narration_complete, result_path)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def analysis_complete(self, result_path):
        """Handle completion of video analysis"""
        self.hide_progress(
            self.analysis_progress,
            self.analysis_status,
            self.analysis_progress_frame
        )
        self.analyze_button.config(state='normal')
        messagebox.showinfo(
            "Success",
            f"Analysis complete!\nResults saved to:\n{result_path}"
        )

    def narration_complete(self, result_path):
        """Handle completion of narration generation"""
        self.hide_progress(
            self.narration_progress,
            self.narration_status,
            self.narration_progress_frame
        )
        self.generate_button.config(state='normal')
        messagebox.showinfo(
            "Success",
            f"Narration generated!\nScript saved to:\n{result_path}"
        )

    def show_error(self, message):
        """Show error message and reset UI"""
        self.hide_progress(
            self.analysis_progress,
            self.analysis_status,
            self.analysis_progress_frame
        )
        self.hide_progress(
            self.narration_progress,
            self.narration_status,
            self.narration_progress_frame
        )
        self.analyze_button.config(state='normal')
        self.generate_button.config(state='normal')
        messagebox.showerror("Error", message)

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoNarratorApp()
    app.run()