"""
Main application for video subtitle extraction, translation, and incorporation.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import click
from tqdm import tqdm

from config import BASE_VIDEOS_DIR, SUBTITLES_DIR, TRANSLATED_SUBTITLES_DIR, OUTPUT_DIR
from modules.subtitle_extractor import SubtitleExtractor
from modules.mcp_client import MCPClient
from modules.video_processor import VideoProcessor


class VideoSubtitleProcessor:
    """Main class that orchestrates the entire subtitle processing workflow."""
    
    def __init__(self):
        self.extractor = SubtitleExtractor()
        self.translator = MCPClient()
        self.processor = VideoProcessor()
        
    def process_single_video(self, video_path: Path, hardcoded: bool = False) -> bool:
        """Process a single video through the entire workflow."""
        print(f"\n{'='*60}")
        print(f"Processing: {video_path.name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Extract subtitles
            print("\n1. Extracting subtitles...")
            extracted_subtitles = self.extractor.extract_all_subtitles(video_path)
            
            if not extracted_subtitles:
                print(f"No subtitles found in {video_path.name}")
                return False
            
            # Step 2: Translate subtitles
            print("\n2. Translating subtitles...")
            translated_subtitles = []
            
            for subtitle_path in extracted_subtitles:
                print(f"   Translating: {subtitle_path.name}")
                translated_path = self.translator.translate_subtitle_file(subtitle_path)
                if translated_path:
                    translated_subtitles.append(translated_path)
                else:
                    print(f"   Failed to translate: {subtitle_path.name}")
            
            if not translated_subtitles:
                print("No subtitles were successfully translated")
                return False
            
            # Step 3: Process video with translated subtitles
            print("\n3. Processing video with translated subtitles...")
            
            # Use the first translated subtitle for now
            # In the future, you could add logic to choose the best subtitle
            subtitle_path = translated_subtitles[0]
            
            result_path = self.processor.process_video_with_subtitle(
                video_path, subtitle_path, hardcoded=hardcoded
            )
            
            if result_path:
                print(f"[OK] Successfully processed: {result_path.name}")
                return True
            else:
                print(f"[ERROR] Failed to process video: {video_path.name}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error processing {video_path.name}: {e}")
            return False
    
    def process_all_videos(self, hardcoded: bool = False) -> Dict[str, bool]:
        """Process all videos in the base_videos directory."""
        video_files = self.extractor.find_video_files()
        
        if not video_files:
            print("No video files found in base_videos directory")
            return {}
        
        print(f"Found {len(video_files)} video file(s) to process")
        print(f"Hardcoded subtitles: {'Yes' if hardcoded else 'No'}")
        
        results = {}
        
        for video_path in tqdm(video_files, desc="Processing videos"):
            success = self.process_single_video(video_path, hardcoded)
            results[video_path.name] = success
        
        return results
    
    def cleanup_working_files(self, keep_subtitles: bool = False):
        """Clean up intermediate working files."""
        if not keep_subtitles:
            print("\nCleaning up working files...")
            
            # Clean up extracted subtitles
            for subtitle_file in SUBTITLES_DIR.glob("*"):
                if subtitle_file.is_file():
                    subtitle_file.unlink()
                    print(f"Cleaned up: {subtitle_file.name}")
            
            # Clean up translated subtitles
            for translated_file in TRANSLATED_SUBTITLES_DIR.glob("*"):
                if translated_file.is_file():
                    translated_file.unlink()
                    print(f"Cleaned up: {translated_file.name}")
        else:
            print("\nKeeping working files for inspection")


@click.command()
@click.option('--video', '-v', help='Process specific video file')
@click.option('--all', '-a', is_flag=True, help='Process all videos in base_videos directory')
@click.option('--hardcoded', '-h', is_flag=True, help='Create hardcoded subtitle videos')
@click.option('--keep-files', '-k', is_flag=True, help='Keep intermediate subtitle files')
@click.option('--test', '-t', is_flag=True, help='Test MCP server connection')
def main(video, all, hardcoded, keep_files, test):
    """Video Subtitle Extractor and Translator using LARA MCP Server."""
    
    if test:
        print("Testing MCP server connection...")
        translator = MCPClient()
        if translator.test_connection():
            print("[OK] MCP server connection successful")
        else:
            print("[ERROR] LARA MCP server connection failed")
        print("Please check your LARA_ACCESS_KEY_ID and LARA_ACCESS_KEY_SECRET configuration")
        return
    
    if not video and not all:
        click.echo("Please specify either --video or --all option")
        click.echo("Use --help for more information")
        return
    
    processor = VideoSubtitleProcessor()
    
    if video:
        # Process single video
        video_path = Path(video)
        if not video_path.exists():
            print(f"Video file not found: {video}")
            return
        
        success = processor.process_single_video(video_path, hardcoded)
        if success:
            print(f"\n[OK] Successfully processed: {video_path.name}")
        else:
            print(f"\n[ERROR] Failed to process: {video_path.name}")
    
    elif all:
        # Process all videos
        results = processor.process_all_videos(hardcoded)
        
        # Summary
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"Total videos: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        
        if successful > 0:
            print(f"\nOutput files saved to: {OUTPUT_DIR}")
        
        # Clean up
        processor.cleanup_working_files(keep_files)


if __name__ == "__main__":
    main()
