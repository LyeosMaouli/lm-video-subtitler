"""
UI components and widget creation for the GUI.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional, Callable


class FolderSelectionFrame(ttk.LabelFrame):
    """Folder selection widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Folder Selection", padding="10", **kwargs)
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.create_widgets()
    
    def create_widgets(self):
        """Create folder selection widgets."""
        self.columnconfigure(1, weight=1)
        
        # Input folder
        ttk.Label(self, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(self, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(self, text="Browse", command=self.browse_input_folder).grid(row=0, column=2)
        
        # Output folder
        ttk.Label(self, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(self, text=tk.StringVar(), textvariable=self.output_folder, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(self, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, pady=(10, 0))
    
    def browse_input_folder(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
    
    def browse_output_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def get_input_folder(self) -> str:
        """Get input folder path."""
        return self.input_folder.get()
    
    def get_output_folder(self) -> str:
        """Get output folder path."""
        return self.output_folder.get()
    
    def set_input_folder(self, path: str):
        """Set input folder path."""
        self.input_folder.set(path)
    
    def set_output_folder(self, path: str):
        """Set output folder path."""
        self.output_folder.set(path)


class QueueFrame(ttk.LabelFrame):
    """Queue management widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Processing Queue", padding="10", **kwargs)
        self.processing_queue = []
        self.create_widgets()
    
    def create_widgets(self):
        """Create queue management widgets."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Queue controls
        queue_controls = ttk.Frame(self)
        queue_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(queue_controls, text="Scan Input Folder", command=self.on_scan).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(queue_controls, text="Clear Queue", command=self.on_clear).pack(side=tk.LEFT)
        
        # Queue treeview
        columns = ("Video File", "Subtitle File", "Status")
        self.queue_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            self.queue_tree.heading(col, text=col)
            self.queue_tree.column(col, width=200)
        
        # Scrollbar for queue
        queue_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)
        
        # Grid queue widgets
        self.queue_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        queue_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to edit subtitle selection
        self.queue_tree.bind("<Double-1>", self.on_double_click)
        
        # Callbacks
        self.on_scan_callback = None
        self.on_clear_callback = None
        self.on_double_click_callback = None
    
    def set_callbacks(self, scan_callback: Callable, clear_callback: Callable, double_click_callback: Callable):
        """Set callback functions."""
        self.on_scan_callback = scan_callback
        self.on_clear_callback = clear_callback
        self.on_double_click_callback = double_click_callback
    
    def on_scan(self):
        """Handle scan button click."""
        if self.on_scan_callback:
            self.on_scan_callback()
    
    def on_clear(self):
        """Handle clear button click."""
        if self.on_clear_callback:
            self.on_clear_callback()
    
    def on_double_click(self, event):
        """Handle double-click on queue items."""
        if self.on_double_click_callback:
            self.on_double_click_callback(event)
    
    def update_queue_display(self, queue_data: List[dict]):
        """Update the queue treeview display."""
        # Clear current display
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        
        # Add items
        for item in queue_data:
            video_name = item['video_path'].name
            subtitle_name = item.get('subtitle_path') or "None (extract only)"
            status = item.get('status', 'Pending')
            
            self.queue_tree.insert("", "end", values=(video_name, subtitle_name, status))
    
    def get_selected_item(self) -> Optional[dict]:
        """Get the currently selected item."""
        selection = self.queue_tree.selection()
        if not selection:
            return None
        
        item = self.queue_tree.item(selection[0])
        values = item['values']
        return {
            'video_name': values[0],
            'subtitle_name': values[1],
            'status': values[2]
        }


class ControlFrame(ttk.LabelFrame):
    """Processing control buttons."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Processing Controls", padding="10", **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        """Create control buttons."""
        # Button row 1
        button_row1 = ttk.Frame(self)
        button_row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_row1, text="Extract & Remove Subtitles", 
                  command=self.on_extract_remove).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="Translate Subtitles", 
                  command=self.on_translate).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="Merge Subtitles", 
                  command=self.on_merge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row1, text="Process All", 
                  command=self.on_process_all).pack(side=tk.LEFT)
        
        # Button row 2
        button_row2 = ttk.Frame(self)
        button_row2.pack(fill=tk.X)
        
        ttk.Button(button_row2, text="Select Subtitles to Translate", 
                  command=self.on_select_subtitles).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row2, text="Stop Processing", 
                  command=self.on_stop).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_row2, text="Open Output Folder", 
                  command=self.on_open_output).pack(side=tk.LEFT)
        
        # Callbacks
        self.on_extract_remove_callback = None
        self.on_translate_callback = None
        self.on_merge_callback = None
        self.on_process_all_callback = None
        self.on_stop_callback = None
        self.on_open_output_callback = None
        self.on_select_subtitles_callback = None
    
    def set_callbacks(self, extract_remove_callback: Callable, translate_callback: Callable, merge_callback: Callable, 
                     process_all_callback: Callable, stop_callback: Callable, open_output_callback: Callable,
                     select_subtitles_callback: Callable):
        """Set callback functions."""
        self.on_extract_remove_callback = extract_remove_callback
        self.on_translate_callback = translate_callback
        self.on_merge_callback = merge_callback
        self.on_process_all_callback = process_all_callback
        self.on_stop_callback = stop_callback
        self.on_open_output_callback = open_output_callback
        self.on_select_subtitles_callback = select_subtitles_callback
    
    def on_extract_remove(self):
        """Handle extract & remove button click."""
        if self.on_extract_remove_callback:
            self.on_extract_remove_callback()
    
    def on_translate(self):
        """Handle translate button click."""
        if self.on_translate_callback:
            self.on_translate_callback()
    
    def on_select_subtitles(self):
        """Handle select subtitles to translate button click."""
        if self.on_select_subtitles_callback:
            self.on_select_subtitles_callback()
    
    def on_merge(self):
        """Handle merge button click."""
        if self.on_merge_callback:
            self.on_merge_callback()
    
    def on_process_all(self):
        """Handle process all button click."""
        if self.on_process_all_callback:
            self.on_process_all_callback()
    
    def on_stop(self):
        """Handle stop button click."""
        if self.on_stop_callback:
            self.on_stop_callback()
    
    def on_open_output(self):
        """Handle open output folder button click."""
        if self.on_open_output_callback:
            self.on_open_output_callback()


class LanguageSelectionFrame(ttk.LabelFrame):
    """Language selection widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Language Settings", padding="10", **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        """Create language selection widgets."""
        self.columnconfigure(1, weight=1)
        
        # Source language
        ttk.Label(self, text="Source Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.source_language = tk.StringVar(value="en")
        source_combo = ttk.Combobox(self, textvariable=self.source_language, width=8, state="readonly")
        source_combo['values'] = ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
        source_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Target language
        ttk.Label(self, text="Target Language:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.target_language = tk.StringVar(value="fr")
        target_combo = ttk.Combobox(self, textvariable=self.target_language, width=8, state="readonly")
        target_combo['values'] = ['fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
        target_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
    
    def get_source_language(self) -> str:
        """Get the selected source language."""
        return self.source_language.get()
    
    def get_target_language(self) -> str:
        """Get the selected target language."""
        return self.target_language.get()
    
    def set_languages(self, source: str, target: str):
        """Set the source and target languages."""
        self.source_language.set(source)
        self.target_language.set(target)


class TranslationFrame(ttk.LabelFrame):
    """Translation testing widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Translation Test", padding="10", **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        """Create translation testing widgets."""
        self.columnconfigure(1, weight=1)
        
        # Language selection
        ttk.Label(self, text="Target Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.target_language = tk.StringVar(value="fr")
        language_combo = ttk.Combobox(self, textvariable=self.target_language, width=8, state="readonly")
        language_combo['values'] = ['fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Test text input
        ttk.Label(self, text="Test Text:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.test_text = tk.StringVar(value="Hello, how are you?")
        ttk.Entry(self, textvariable=self.test_text, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(self, text="Test Translation", command=self.on_test).grid(row=1, column=2, pady=(10, 0))
        
        # Connection test button
        ttk.Button(self, text="Test Connection", command=self.on_test_connection).grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        
        # Translation result
        self.translation_result = tk.StringVar()
        ttk.Label(self, text="Result:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(self, textvariable=self.translation_result, width=50, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Callbacks
        self.on_test_callback = None
        self.on_test_connection_callback = None
    
    def set_callbacks(self, test_callback: Callable, test_connection_callback: Callable = None):
        """Set callback functions."""
        self.on_test_callback = test_callback
        self.on_test_connection_callback = test_connection_callback
    
    def on_test(self):
        """Handle test translation button click."""
        if self.on_test_callback:
            self.on_test_callback()
    
    def on_test_connection(self):
        """Handle test connection button click."""
        if self.on_test_connection_callback:
            self.on_test_connection_callback()
    
    def get_test_text(self) -> str:
        """Get the test text."""
        return self.test_text.get()
    
    def set_translation_result(self, result: str):
        """Set the translation result."""
        self.translation_result.set(result)
    
    def get_target_language(self) -> str:
        """Get the selected target language."""
        return self.target_language.get()


class StatusFrame(ttk.LabelFrame):
    """Status display widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Status", padding="10", **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        """Create status display widgets."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Status text
        self.status_text = tk.Text(self, height=8, wrap=tk.WORD)
        status_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def log_message(self, message: str):
        """Log a message to the status text."""
        import time
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
    
    def set_progress(self, value: float):
        """Set progress bar value."""
        self.progress_var.set(value)
    
    def clear_log(self):
        """Clear the status log."""
        self.status_text.delete(1.0, tk.END)


class SubtitleSelectionDialog:
    """Dialog for selecting subtitle files."""
    
    def __init__(self, parent, subtitle_files: List[Path], video_name: str):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Select Subtitle for {video_name}")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.subtitle_files = subtitle_files
        self.selected_subtitle = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Subtitle list
        ttk.Label(self.dialog, text="Select subtitle file:").pack(pady=10)
        
        self.subtitle_listbox = tk.Listbox(self.dialog, height=10)
        self.subtitle_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add subtitle options
        self.subtitle_listbox.insert(0, "None (extract only)")
        for subtitle_file in self.subtitle_files:
            self.subtitle_listbox.insert(tk.END, subtitle_file.name)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Select", command=self.on_select).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)
    
    def on_select(self):
        """Handle select button click."""
        selection = self.subtitle_listbox.curselection()
        if selection:
            if selection[0] == 0:
                self.selected_subtitle = None
            else:
                self.selected_subtitle = self.subtitle_files[selection[0] - 1].name
            self.dialog.destroy()
    
    def on_cancel(self):
        """Handle cancel button click."""
        self.dialog.destroy()
    
    def get_result(self) -> Optional[str]:
        """Get the selected subtitle."""
        return self.selected_subtitle
    
    def show(self) -> Optional[str]:
        """Show the dialog and return the result."""
        self.dialog.wait_window()
        return self.selected_subtitle
