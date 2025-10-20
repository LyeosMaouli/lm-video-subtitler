"""
Refactored GUI application for Video Subtitle Extractor and Translator.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
import threading

from modules.core_processor import CoreProcessor
from modules.settings_manager import SettingsManager
from modules.ui_components import (
    FolderSelectionFrame, QueueFrame, ControlFrame, 
    TranslationFrame, StatusFrame, SubtitleSelectionDialog,
    LanguageSelectionFrame
)


class VideoSubtitleGUI:
    """Main GUI application for video subtitle processing."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitle Processor")
        self.root.geometry("1000x900")
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.core_processor = CoreProcessor()
        
        # Create UI
        self.create_widgets()
        
        # Load settings
        self.load_settings()
        
        # Set up callbacks
        self.setup_callbacks()
        
        # Check translator status on startup
        self.check_translator_status()
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Create UI components
        self.folder_frame = FolderSelectionFrame(main_frame)
        self.folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.language_frame = LanguageSelectionFrame(main_frame)
        self.language_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.queue_frame = QueueFrame(main_frame)
        self.queue_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.control_frame = ControlFrame(main_frame)
        self.control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.translation_frame = TranslationFrame(main_frame)
        self.translation_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_frame = StatusFrame(main_frame)
        self.status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_callbacks(self):
        """Set up callback functions for UI components."""
        # Queue frame callbacks
        self.queue_frame.set_callbacks(
            scan_callback=self.scan_input_folder,
            clear_callback=self.clear_queue,
            double_click_callback=self.on_queue_double_click
        )
        
        # Control frame callbacks
        self.control_frame.set_callbacks(
            extract_remove_callback=self.extract_and_remove_subtitles,
            translate_callback=self.translate_subtitles,
            select_subtitles_callback=self.select_subtitles_to_translate,
            merge_callback=self.merge_subtitles,
            process_all_callback=self.process_all,
            stop_callback=self.stop_processing,
            open_output_callback=self.open_output_folder
        )
        
        # Translation frame callbacks
        self.translation_frame.set_callbacks(
            test_callback=self.test_translation,
            test_connection_callback=self.test_connection
        )
        
        # Sync language settings when they change
        self.language_frame.source_language.trace('w', self._on_language_changed)
        self.language_frame.target_language.trace('w', self._on_language_changed)
    
    def load_settings(self):
        """Load application settings."""
        # Load folder paths
        input_folder = self.settings_manager.get('input_folder', '')
        output_folder = self.settings_manager.get('output_folder', '')
        
        if input_folder:
            self.folder_frame.set_input_folder(input_folder)
        if output_folder:
            self.folder_frame.set_output_folder(output_folder)
        
        # Load translation settings
        translation_settings = self.settings_manager.get_translation_settings()
        if translation_settings.get('test_text'):
            # Note: We can't directly set the test_text in the frame yet
            # This would need a setter method in TranslationFrame
            pass
    
    def save_folder_settings(self):
        """Save current folder settings."""
        input_folder = self.folder_frame.get_input_folder()
        output_folder = self.folder_frame.get_output_folder()
        
        if input_folder:
            self.settings_manager.set('input_folder', input_folder)
            self.settings_manager.add_recent_folder('input', input_folder)
        
        if output_folder:
            self.settings_manager.set('output_folder', output_folder)
            self.settings_manager.add_recent_folder('output', output_folder)
    
    def scan_input_folder(self):
        """Scan input folder for videos and matching subtitles."""
        input_path = Path(self.folder_frame.get_input_folder())
        if not input_path.exists():
            messagebox.showerror("Error", "Input folder does not exist!")
            return
        
        try:
            # Use core processor to scan
            queue_data = self.core_processor.scan_input_folder(input_path)
            
            if not queue_data:
                messagebox.showinfo("Info", "No video files found in input folder!")
                return
            
            # Update queue display
            self.queue_frame.update_queue_display(queue_data)
            
            # Count items with subtitles
            items_with_subtitles = len([q for q in queue_data if q.get('subtitle_path')])
            self.status_frame.log_message(f"Scanned {len(queue_data)} video files, {items_with_subtitles} with matching subtitles")
            
            # Save settings
            self.save_folder_settings()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan input folder: {e}")
    
    def clear_queue(self):
        """Clear the processing queue."""
        self.core_processor.clear_queue()
        self.queue_frame.update_queue_display([])
        self.status_frame.log_message("Queue cleared")
    
    def on_queue_double_click(self, event):
        """Handle double-click on queue items to edit subtitle selection."""
        selected_item = self.queue_frame.get_selected_item()
        if not selected_item:
            return
        
        video_name = selected_item['video_name']
        input_path = Path(self.folder_frame.get_input_folder())
        
        try:
            # Get available subtitles
            subtitle_files = self.core_processor.get_available_subtitles(input_path)
            
            if not subtitle_files:
                messagebox.showinfo("Info", "No subtitle files found!")
                return
            
            # Show subtitle selection dialog
            dialog = SubtitleSelectionDialog(self.root, subtitle_files, video_name)
            selected_subtitle = dialog.show()
            
            if selected_subtitle is not None:
                # Update the core processor
                self.core_processor.set_subtitle_for_video(video_name, selected_subtitle)
                
                # Update display
                queue_data = self.core_processor.get_queue()
                self.queue_frame.update_queue_display(queue_data)
                
                self.status_frame.log_message(f"Updated subtitle for {video_name}: {selected_subtitle or 'None'}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update subtitle selection: {e}")
    
    def extract_and_remove_subtitles(self):
        """Extract subtitles and create videos without subtitles."""
        if not self.core_processor.get_queue():
            messagebox.showwarning("Warning", "Queue is empty! Please scan input folder first.")
            return
        
        output_path = Path(self.folder_frame.get_output_folder())
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Set the output directory in the core processor
        self.core_processor.set_output_directory(output_path)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._extract_and_remove_worker, args=(output_path,))
        thread.daemon = True
        thread.start()
    
    def _extract_and_remove_worker(self, output_path: Path):
        """Worker thread for subtitle extraction and removal."""
        try:
            # Progress callback
            def progress_callback(message: str, progress: float):
                self.root.after(0, lambda: self.status_frame.log_message(message))
                self.root.after(0, lambda: self.status_frame.set_progress(progress))
            
            # Status callback
            def status_callback(video_name: str, status: str):
                self.root.after(0, lambda: self.status_frame.log_message(f"{video_name}: {status}"))
            
            # Process
            results = self.core_processor.extract_and_remove_subtitles(
                output_path, progress_callback, status_callback
            )
            
            # Update queue display
            queue_data = self.core_processor.get_queue()
            self.root.after(0, lambda: self.queue_frame.update_queue_display(queue_data))
            
            # Log results
            for result in results:
                if result['status'] == 'Completed':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"✅ {r['video']}: {r.get('subtitles_extracted', 0)} subtitles extracted"
                    ))
                elif result['status'] == 'Error':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"❌ {r['video']}: {r.get('error', 'Unknown error')}"
                    ))
            
            self.root.after(0, lambda: self.status_frame.set_progress(100))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_frame.log_message(f"Processing error: {e}"))
    
    def _translate_worker(self, source_lang: str, target_lang: str):
        """Worker thread for subtitle translation."""
        try:
            # Progress callback
            def progress_callback(message: str, progress: float):
                self.root.after(0, lambda: self.status_frame.log_message(message))
                self.root.after(0, lambda: self.status_frame.set_progress(progress))
            
            # Status callback
            def status_callback(video_name: str, status: str):
                self.root.after(0, lambda: self.status_frame.log_message(f"{video_name}: {status}"))
            
            # Process translation
            results = self.core_processor.translate_subtitles(
                source_lang, target_lang, progress_callback, status_callback
            )
            
            # Update queue display
            queue_data = self.core_processor.get_queue()
            self.root.after(0, lambda: self.queue_frame.update_queue_display(queue_data))
            
            # Log results
            for result in results:
                if result['status'] == 'Completed':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"✅ {r['video']}: Subtitles translated successfully"
                    ))
                elif result['status'] == 'Error':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"❌ {r['video']}: {r.get('error', 'Unknown error')}"
                    ))
            
            self.root.after(0, lambda: self.status_frame.set_progress(100))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_frame.log_message(f"Translation error: {e}"))
    
    def select_subtitles_to_translate(self):
        """Open subtitle selection dialog for translation."""
        if not self.core_processor.get_queue():
            messagebox.showwarning("Warning", "Queue is empty! Please scan input folder first.")
            return
        
        # Get available subtitles from subtitles folder
        subtitles_dir = Path("subtitles")
        if not subtitles_dir.exists():
            messagebox.showinfo("Info", "No subtitles folder found! Please extract subtitles first.")
            return
        
        subtitle_files = []
        for ext in ['.srt', '.ass', '.ssa']:
            subtitle_files.extend(subtitles_dir.glob(f"*{ext}"))
        
        if not subtitle_files:
            messagebox.showinfo("Info", "No subtitle files found in subtitles folder!")
            return
        
        # Show subtitle selection dialog
        dialog = SubtitleSelectionDialog(self.root, subtitle_files, "Translation")
        selected_subtitles = dialog.show_multiple()
        
        if selected_subtitles:
            # Update the queue to only include selected subtitles for translation
            self.core_processor.set_subtitles_for_translation(selected_subtitles)
            
            # Update display
            queue_data = self.core_processor.get_queue()
            self.queue_frame.update_queue_display(queue_data)
            
            self.status_frame.log_message(f"Selected {len(selected_subtitles)} subtitles for translation")
    
    def translate_subtitles(self):
        """Translate existing subtitle files."""
        if not self.core_processor.get_queue():
            messagebox.showwarning("Warning", "Queue is empty! Please scan input folder first.")
            return
        
        # Check if we have subtitles to translate
        items_with_subtitles = [q for q in self.core_processor.get_queue() if q.get('subtitle_path')]
        if not items_with_subtitles:
            messagebox.showinfo("Info", "No subtitles found to translate! Please scan input folder first.")
            return
        
        # Get language settings
        source_lang = self.language_frame.get_source_language()
        target_lang = self.language_frame.get_target_language()
        
        if source_lang == target_lang:
            messagebox.showwarning("Warning", "Source and target languages are the same!")
            return
        
        # Confirm translation
        count = len(items_with_subtitles)
        if not messagebox.askyesno("Confirm Translation", 
                                 f"Translate {count} subtitle files from {source_lang} to {target_lang}?"):
            return
        
        # Start translation in background thread
        thread = threading.Thread(target=self._translate_worker, args=(source_lang, target_lang))
        thread.daemon = True
        thread.start()
    
    def merge_subtitles(self):
        """Merge selected subtitles with videos."""
        if not self.core_processor.get_queue():
            messagebox.showwarning("Warning", "Queue is empty! Please scan input folder first.")
            return
        
        input_path = Path(self.folder_frame.get_input_folder())
        output_path = Path(self.folder_frame.get_output_folder())
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Set the output directory in the core processor
        self.core_processor.set_output_directory(output_path)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._merge_worker, args=(input_path, output_path))
        thread.daemon = True
        thread.start()
    
    def _merge_worker(self, input_path: Path, output_path: Path):
        """Worker thread for subtitle merging."""
        try:
            # Progress callback
            def progress_callback(message: str, progress: float):
                self.root.after(0, lambda: self.status_frame.log_message(message))
                self.root.after(0, lambda: self.status_frame.set_progress(progress))
            
            # Status callback
            def status_callback(video_name: str, status: str):
                self.root.after(0, lambda: self.status_frame.log_message(f"{video_name}: {status}"))
            
            # Process
            results = self.core_processor.merge_subtitles(
                input_path, output_path, progress_callback, status_callback
            )
            
            # Update queue display
            queue_data = self.core_processor.get_queue()
            self.root.after(0, lambda: self.queue_frame.update_queue_display(queue_data))
            
            # Log results
            for result in results:
                if result['status'] == 'Completed':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"✅ {r['video']}: Subtitles merged successfully"
                    ))
                elif result['status'] == 'Error':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"❌ {r['video']}: {r.get('error', 'Unknown error')}"
                    ))
            
            self.root.after(0, lambda: self.status_frame.set_progress(100))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_frame.log_message(f"Processing error: {e}"))
    
    def process_all(self):
        """Process all items in queue (extract + merge if subtitle selected)."""
        if not self.core_processor.get_queue():
            messagebox.showwarning("Warning", "Queue is empty! Please scan input folder first.")
            return
        
        input_path = Path(self.folder_frame.get_input_folder())
        output_path = Path(self.folder_frame.get_output_folder())
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Set the output directory in the core processor
        self.core_processor.set_output_directory(output_path)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._process_all_worker, args=(input_path, output_path))
        thread.daemon = True
        thread.start()
    
    def _process_all_worker(self, input_path: Path, output_path: Path):
        """Worker thread for processing all items."""
        try:
            # Progress callback
            def progress_callback(message: str, progress: float):
                self.root.after(0, lambda: self.status_frame.log_message(message))
                self.root.after(0, lambda: self.status_frame.set_progress(progress))
            
            # Status callback
            def status_callback(video_name: str, status: str):
                self.root.after(0, lambda: self.status_frame.log_message(f"{video_name}: {status}"))
            
            # Process
            results = self.core_processor.process_all(
                input_path, output_path, progress_callback, status_callback
            )
            
            # Update queue display
            queue_data = self.core_processor.get_queue()
            self.root.after(0, lambda: self.queue_frame.update_queue_display(queue_data))
            
            # Log results
            for result in results:
                if result['status'] == 'Completed':
                    action = result.get('action', 'processed')
                    if action == 'merged_subtitles':
                        self.root.after(0, lambda r=result: self.status_frame.log_message(
                            f"✅ {r['video']}: Subtitles merged successfully"
                        ))
                    elif action == 'extracted_subtitles':
                        self.root.after(0, lambda r=result: self.status_frame.log_message(
                            f"✅ {r['video']}: {r.get('subtitles_count', 0)} subtitles extracted"
                        ))
                elif result['status'] == 'Error':
                    self.root.after(0, lambda r=result: self.status_frame.log_message(
                        f"❌ {r['video']}: {r.get('error', 'Unknown error')}"
                    ))
            
            self.root.after(0, lambda: self.status_frame.set_progress(100))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_frame.log_message(f"Processing error: {e}"))
    
    def stop_processing(self):
        """Stop all processing."""
        self.core_processor.stop_all_processing()
        
        # Update queue display
        queue_data = self.core_processor.get_queue()
        self.queue_frame.update_queue_display(queue_data)
        
        self.status_frame.log_message("Processing stopped by user")
    
    def open_output_folder(self):
        """Open output folder in file explorer."""
        output_path = Path(self.folder_frame.get_output_folder())
        if output_path.exists():
            os.startfile(output_path)
        else:
            messagebox.showwarning("Warning", "Output folder does not exist!")
    
    def test_translation(self):
        """Test translation with the entered text."""
        text = self.translation_frame.get_test_text().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate!")
            return
        
        # Get selected languages
        source_lang = self.language_frame.get_source_language()
        target_lang = self.language_frame.get_target_language()
        
        self.status_frame.log_message(f"Testing translation: {text} ({source_lang} → {target_lang})")
        
        # Start translation test in background thread
        thread = threading.Thread(target=self._test_translation_worker, args=(text, source_lang, target_lang))
        thread.daemon = True
        thread.start()
    
    def _test_translation_worker(self, text: str, source_lang: str, target_lang: str):
        """Worker thread for translation testing."""
        try:
            print(f"🔧 DEBUG: GUI translation worker called with: '{text}' ({source_lang} -> {target_lang})")
            translated = self.core_processor.test_translation(text, source_lang, target_lang)
            print(f"🔧 DEBUG: GUI translation worker received: '{translated}'")
            
            if translated:
                self.root.after(0, lambda: self.translation_frame.set_translation_result(translated))
                self.root.after(0, lambda: self.status_frame.log_message(f"Translation successful: {translated}"))
            else:
                self.root.after(0, lambda: self.translation_frame.set_translation_result("Translation failed"))
                self.root.after(0, lambda: self.status_frame.log_message("Translation failed"))
        
        except Exception as e:
            print(f"🔧 DEBUG: GUI translation worker error: {e}")
            self.root.after(0, lambda: self.translation_frame.set_translation_result("Translation error"))
            self.root.after(0, lambda: self.status_frame.log_message(f"Translation error: {e}"))
    
    def check_translator_status(self):
        """Check and display translator credential status."""
        try:
            status = self.core_processor.get_translator_status()
            
            if status['configured']:
                self.status_frame.log_message("✅ LARA credentials configured successfully")
                
                # Test connection in background
                thread = threading.Thread(target=self._test_connection_worker)
                thread.daemon = True
                thread.start()
            else:
                self.status_frame.log_message("❌ LARA credentials not properly configured")
                self.status_frame.log_message(f"   Missing: {', '.join([k for k, v in status.items() if 'present' in k and not v])}")
                self.status_frame.log_message("   Please check your .env file")
                
        except Exception as e:
            self.status_frame.log_message(f"❌ Error checking translator status: {e}")
    
    def test_connection(self):
        """Test the connection to the LARA MCP server."""
        self.status_frame.log_message("Testing LARA MCP server connection...")
        
        # Start connection test in background thread
        thread = threading.Thread(target=self._test_connection_worker)
        thread.daemon = True
        thread.start()
    
    def _test_connection_worker(self):
        """Worker thread to test LARA MCP server connection."""
        try:
            if self.core_processor.test_translator_connection():
                self.root.after(0, lambda: self.status_frame.log_message("✅ LARA MCP server connection successful"))
            else:
                self.root.after(0, lambda: self.status_frame.log_message("❌ LARA MCP server connection failed"))
                self.root.after(0, lambda: self.status_frame.log_message("   Check server URL and network connectivity"))
        except Exception as e:
            self.root.after(0, lambda: self.status_frame.log_message(f"❌ Connection test error: {e}"))
    
    def _on_language_changed(self, *args):
        """Handle language selection changes."""
        try:
            source_lang = self.language_frame.get_source_language()
            target_lang = self.language_frame.get_target_language()
            
            # Update core processor language settings
            self.core_processor.set_language_settings(source_lang, target_lang)
            
            # Update translation frame target language to match
            self.translation_frame.target_language.set(target_lang)
            
            self.status_frame.log_message(f"Language settings updated: {source_lang} → {target_lang}")
            
        except Exception as e:
            self.status_frame.log_message(f"Error updating language settings: {e}")


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = VideoSubtitleGUI(root)
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
