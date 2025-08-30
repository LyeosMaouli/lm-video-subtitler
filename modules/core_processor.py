"""
Core video processing logic separated from GUI.
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
import threading
from queue import Queue

from config import SUPPORTED_VIDEO_FORMATS, SUPPORTED_SUBTITLE_FORMATS
from .subtitle_extractor import SubtitleExtractor
from .mcp_client import MCPClient
from .video_processor import VideoProcessor


class CoreProcessor:
    """Core video processing logic separated from GUI."""
    
    def __init__(self):
        self.extractor = SubtitleExtractor()
        self.translator = MCPClient()
        self.processor = VideoProcessor()
        self.processing_queue = []
        self.queue_lock = threading.Lock()
        self.stop_processing = False
        
    def set_output_directory(self, output_path: Path):
        """Set the output directory for video processing."""
        self.processor.set_output_directory(output_path)
        
    def scan_input_folder(self, input_path: Path) -> List[Dict]:
        """Scan input folder for videos and matching subtitles."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input folder does not exist: {input_path}")
        
        # Update subtitle extractor with the input directory
        self.extractor.set_input_directory(input_path)
        
        # Clear current queue
        self.processing_queue.clear()
        
        # Find video files
        video_files = []
        for ext in SUPPORTED_VIDEO_FORMATS:
            video_files.extend(input_path.glob(f"*{ext}"))
        
        if not video_files:
            return []
        
        # Find matching subtitle files in the subtitles directory
        subtitle_files = []
        subtitles_dir = Path("subtitles")
        if subtitles_dir.exists():
            for ext in SUPPORTED_SUBTITLE_FORMATS:
                subtitle_files.extend(subtitles_dir.glob(f"*{ext}"))
        
        # Build queue
        for video_file in sorted(video_files):
            video_name = video_file.stem
            matching_subtitle = None
            
            # Look for matching subtitle
            for subtitle_file in subtitle_files:
                subtitle_stem = subtitle_file.stem
                # Check if subtitle filename starts with video name (handles _subtitle_X suffix)
                if subtitle_stem.startswith(video_name):
                    matching_subtitle = subtitle_file.name
                    break
            
            # Add to queue
            self.processing_queue.append({
                'video_path': video_file,
                'subtitle_path': matching_subtitle,
                'status': 'Pending'
            })
        
        return self.processing_queue.copy()
    
    def get_queue(self) -> List[Dict]:
        """Get current processing queue."""
        with self.queue_lock:
            return self.processing_queue.copy()
    
    def update_item_status(self, video_name: str, status: str):
        """Update status of a specific queue item."""
        with self.queue_lock:
            for item in self.processing_queue:
                if item['video_path'].name == video_name:
                    item['status'] = status
                    break
    
    def set_subtitle_for_video(self, video_name: str, subtitle_name: Optional[str]):
        """Set subtitle for a specific video."""
        with self.queue_lock:
            for item in self.processing_queue:
                if item['video_path'].name == video_name:
                    item['subtitle_path'] = subtitle_name
                    break
    
    def set_subtitles_for_translation(self, selected_subtitles: List[str]):
        """Set which subtitles should be used for translation."""
        with self.queue_lock:
            # Clear all subtitle selections first
            for item in self.processing_queue:
                item['subtitle_path'] = None
            
            # Set only the selected subtitles
            for subtitle_name in selected_subtitles:
                # Find which video this subtitle belongs to
                for item in self.processing_queue:
                    video_name = item['video_path'].stem
                    if subtitle_name.startswith(video_name):
                        item['subtitle_path'] = subtitle_name
                        break
    
    def clear_queue(self):
        """Clear the processing queue."""
        with self.queue_lock:
            self.processing_queue.clear()
    
    def extract_and_remove_subtitles(self, output_path: Path, 
                                   progress_callback: Callable[[str, float], None] = None,
                                   status_callback: Callable[[str, str], None] = None) -> List[Dict]:
        """Extract subtitles and create videos without subtitles."""
        if not self.processing_queue:
            raise ValueError("Queue is empty! Please scan input folder first.")
        
        results = []
        total = len(self.processing_queue)
        
        for i, item in enumerate(self.processing_queue):
            if self.stop_processing:
                break
            
            video_name = item['video_path'].name
            self.update_item_status(video_name, 'Processing')
            
            if progress_callback:
                progress_callback(f"Processing {video_name} ({i+1}/{total})", (i / total) * 100)
            
            try:
                # Extract subtitles
                extracted_subtitles = self.extractor.extract_all_subtitles(item['video_path'])
                
                if extracted_subtitles:
                    if status_callback:
                        status_callback(video_name, f"Extracted {len(extracted_subtitles)} subtitle tracks")
                    
                    # Create video without subtitles
                    output_file = output_path / f"{item['video_path'].stem}_no_subtitles.mkv"
                    result = self.processor.create_video_without_subtitles(item['video_path'], output_file)
                    
                    if result:
                        self.update_item_status(video_name, 'Completed')
                        results.append({
                            'video': video_name,
                            'status': 'Completed',
                            'output': str(output_file),
                            'subtitles_extracted': len(extracted_subtitles)
                        })
                    else:
                        self.update_item_status(video_name, 'Error')
                        results.append({
                            'video': video_name,
                            'status': 'Error',
                            'error': 'Failed to create video without subtitles'
                        })
                else:
                    self.update_item_status(video_name, 'No Subtitles')
                    results.append({
                        'video': video_name,
                        'status': 'No Subtitles',
                        'message': 'No subtitles found'
                    })
            
            except Exception as e:
                self.update_item_status(video_name, 'Error')
                results.append({
                    'video': video_name,
                    'status': 'Error',
                    'error': str(e)
                })
        
        if progress_callback:
            progress_callback("Subtitle extraction and removal completed!", 100)
        
        return results
    
    def translate_subtitles(self, source_lang: str, target_lang: str,
                          progress_callback: Callable[[str, float], None] = None,
                          status_callback: Callable[[str, str], None] = None) -> List[Dict]:
        """Translate existing subtitle files."""
        if not self.processing_queue:
            raise ValueError("Queue is empty! Please scan input folder first.")
        
        results = []
        items_with_subtitles = [item for item in self.processing_queue if item['subtitle_path']]
        total = len(items_with_subtitles)
        
        if not items_with_subtitles:
            raise ValueError("No subtitles found to translate!")
        
        for i, item in enumerate(items_with_subtitles):
            if self.stop_processing:
                break
            
            video_name = item['video_path'].name
            subtitle_name = item['subtitle_path']
            self.update_item_status(video_name, 'Translating')
            
            if progress_callback:
                progress_callback(f"Translating {video_name} ({i+1}/{total})", (i / total) * 100)
            
            try:
                # Get subtitle file path
                subtitle_path = Path("subtitles") / subtitle_name
                if not subtitle_path.exists():
                    raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
                
                # Read subtitle content
                subtitle_content = subtitle_path.read_text(encoding='utf-8')
                
                # Translate subtitle using the new SRT-aware method
                translated_content = self.translator.translate_srt_content(subtitle_content, source_lang, target_lang)
                
                if translated_content:
                    # Create translated subtitle filename
                    translated_name = subtitle_name.replace('.srt', f'_{target_lang}.srt')
                    translated_path = Path("subtitles") / translated_name
                    
                    # Write translated content
                    translated_path.write_text(translated_content, encoding='utf-8')
                    
                    # Update queue item to include translated subtitle
                    item['translated_subtitle_path'] = translated_name
                    
                    self.update_item_status(video_name, 'Translated')
                    results.append({
                        'video': video_name,
                        'status': 'Completed',
                        'original_subtitle': subtitle_name,
                        'translated_subtitle': translated_name
                    })
                    
                    if status_callback:
                        status_callback(video_name, f"Translated to {target_lang}")
                else:
                    raise ValueError("Translation returned empty content")
                    
            except Exception as e:
                self.update_item_status(video_name, 'Error')
                results.append({
                    'video': video_name,
                    'status': 'Error',
                    'error': str(e)
                })
                
                if status_callback:
                    status_callback(video_name, f"Translation failed: {e}")
        
        if progress_callback:
            progress_callback("Subtitle translation completed!", 100)
        
        return results
    
    def merge_subtitles(self, input_path: Path, output_path: Path,
                       progress_callback: Callable[[str, float], None] = None,
                       status_callback: Callable[[str, str], None] = None) -> List[Dict]:
        """Merge selected subtitles with videos."""
        items_with_subtitles = [item for item in self.processing_queue if item['subtitle_path']]
        if not items_with_subtitles:
            raise ValueError("No videos have subtitles selected for merging!")
        
        results = []
        total = len(items_with_subtitles)
        
        for i, item in enumerate(items_with_subtitles):
            if self.stop_processing:
                break
            
            video_name = item['video_path'].name
            self.update_item_status(video_name, 'Processing')
            
            if progress_callback:
                progress_callback(f"Merging subtitles for {video_name} ({i+1}/{total})", (i / total) * 100)
            
            try:
                video_path = item['video_path']
                # Look for subtitle in the subtitles folder, not input_path
                subtitle_path = Path("subtitles") / item['subtitle_path']
                
                if not subtitle_path.exists():
                    raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
                
                # Merge subtitle with video
                output_file = output_path / f"{video_path.stem}_with_subtitles.mkv"
                result = self.processor.incorporate_subtitle(video_path, subtitle_path, output_file)
                
                if result:
                    self.update_item_status(video_name, 'Completed')
                    results.append({
                        'video': video_name,
                        'status': 'Completed',
                        'output': str(output_file),
                        'subtitle': item['subtitle_path']
                    })
                else:
                    self.update_item_status(video_name, 'Error')
                    results.append({
                        'video': video_name,
                        'status': 'Error',
                        'error': 'Failed to merge subtitles'
                    })
            
            except Exception as e:
                self.update_item_status(video_name, 'Error')
                results.append({
                    'video': video_name,
                    'status': 'Error',
                    'error': str(e)
                })
        
        if progress_callback:
            progress_callback("Subtitle merging completed!", 100)
        
        return results
    
    def process_all(self, input_path: Path, output_path: Path,
                   progress_callback: Callable[[str, float], None] = None,
                   status_callback: Callable[[str, str], None] = None) -> List[Dict]:
        """Process all items in queue (extract + merge if subtitle selected)."""
        if not self.processing_queue:
            raise ValueError("Queue is empty! Please scan input folder first.")
        
        results = []
        total = len(self.processing_queue)
        
        for i, item in enumerate(self.processing_queue):
            if self.stop_processing:
                break
            
            video_name = item['video_path'].name
            self.update_item_status(video_name, 'Processing')
            
            if progress_callback:
                progress_callback(f"Processing {video_name} ({i+1}/{total})", (i / total) * 100)
            
            try:
                video_path = item['video_path']
                
                if item['subtitle_path']:
                    # Merge subtitle
                    subtitle_path = input_path / item['subtitle_path']
                    output_file = output_path / f"{video_path.stem}_with_subtitles.mkv"
                    result = self.processor.incorporate_subtitle(video_path, subtitle_path, output_file)
                    
                    if result:
                        self.update_item_status(video_name, 'Completed')
                        results.append({
                            'video': video_name,
                            'status': 'Completed',
                            'output': str(output_file),
                            'action': 'merged_subtitles',
                            'subtitle': item['subtitle_path']
                        })
                    else:
                        self.update_item_status(video_name, 'Error')
                        results.append({
                            'video': video_name,
                            'status': 'Error',
                            'error': 'Failed to merge subtitles'
                        })
                else:
                    # Extract subtitles only
                    extracted_subtitles = self.extractor.extract_all_subtitles(video_path)
                    
                    if extracted_subtitles:
                        self.update_item_status(video_name, 'Completed')
                        results.append({
                            'video': video_name,
                            'status': 'Completed',
                            'action': 'extracted_subtitles',
                            'subtitles_count': len(extracted_subtitles)
                        })
                    else:
                        self.update_item_status(video_name, 'No Subtitles')
                        results.append({
                            'video': video_name,
                            'status': 'No Subtitles',
                            'message': 'No subtitles found'
                        })
            
            except Exception as e:
                self.update_item_status(video_name, 'Error')
                results.append({
                    'video': video_name,
                    'status': 'Error',
                    'error': str(e)
                })
        
        if progress_callback:
            progress_callback("All processing completed!", 100)
        
        return results
    
    def stop_all_processing(self):
        """Stop all processing."""
        self.stop_processing = True
        with self.queue_lock:
            for item in self.processing_queue:
                if item['status'] == 'Processing':
                    item['status'] = 'Stopped'
    
    def reset_processing_state(self):
        """Reset processing state for new operations."""
        self.stop_processing = False
        with self.queue_lock:
            for item in self.processing_queue:
                if item['status'] in ['Processing', 'Stopped']:
                    item['status'] = 'Pending'
    
    def test_translation(self, text: str, source_lang: str = "en", target_lang: str = "fr") -> Optional[str]:
        """Test translation with the given text."""
        try:
            return self.translator.translate_text(text, source_lang, target_lang)
        except Exception as e:
            raise Exception(f"Translation failed: {e}")
    
    def get_translator_status(self) -> Dict[str, any]:
        """Get the status of the translator and credentials."""
        return self.translator.get_credential_status()
    
    def test_translator_connection(self) -> bool:
        """Test the connection to the LARA MCP server."""
        return self.translator.test_connection()
    
    def get_available_subtitles(self, input_path: Path) -> List[Path]:
        """Get list of available subtitle files in input folder."""
        subtitle_files = []
        for ext in SUPPORTED_SUBTITLE_FORMATS:
            subtitle_files.extend(input_path.glob(f"*{ext}"))
        return sorted(subtitle_files)
    
    def set_language_settings(self, source_lang: str, target_lang: str):
        """Set the source and target languages for translation."""
        self.source_language = source_lang
        self.target_language = target_lang
    
    def get_language_settings(self) -> Dict[str, str]:
        """Get the current language settings."""
        return {
            'source_language': getattr(self, 'source_language', 'en'),
            'target_language': getattr(self, 'target_language', 'fr')
        }
