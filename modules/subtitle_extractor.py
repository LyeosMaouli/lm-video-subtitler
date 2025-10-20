"""
Subtitle extraction module for video files.
"""
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import ffmpeg
import os
from config import BASE_VIDEOS_DIR, SUBTITLES_DIR, SUPPORTED_VIDEO_FORMATS, SUPPORTED_SUBTITLE_FORMATS, FFMPEG_PATH


class SubtitleExtractor:
    """Handles extraction of subtitles from video files."""
    
    def __init__(self):
        self.base_videos_dir = BASE_VIDEOS_DIR  # Default fallback
        self.subtitles_dir = SUBTITLES_DIR
        
        # Configure FFmpeg path by adding to PATH
        if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
            # Check if both executables exist
            ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
            ffprobe_exe = os.path.join(FFMPEG_PATH, "ffprobe.exe")
            
            if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
                if FFMPEG_PATH not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ.get('PATH', '')
                # Only print once per class instance
                print(f"[OK] SubtitleExtractor: FFmpeg configured")
            else:
                print(f"! SubtitleExtractor: Missing FFmpeg executables in {FFMPEG_PATH}")
        else:
            print(f"! SubtitleExtractor: FFmpeg directory not found at {FFMPEG_PATH}")
        
    def get_video_info(self, video_path: Path) -> Dict:
        """Get information about a video file including available subtitle tracks."""
        try:
            probe = ffmpeg.probe(str(video_path))
            return probe
        except ffmpeg.Error as e:
            print(f"Error probing video {video_path}: {e}")
            return {}
    
    def list_subtitle_tracks(self, video_path: Path) -> List[Dict]:
        """List all available subtitle tracks in a video file."""
        info = self.get_video_info(video_path)
        subtitle_tracks = []
        
        if 'streams' in info:
            for stream in info['streams']:
                if stream.get('codec_type') == 'subtitle':
                    subtitle_tracks.append({
                        'index': stream.get('index'),
                        'codec_name': stream.get('codec_name'),
                        'language': stream.get('tags', {}).get('language', 'unknown'),
                        'title': stream.get('tags', {}).get('title', ''),
                        'codec_long_name': stream.get('codec_long_name', '')
                    })
        
        return subtitle_tracks
    
    def extract_subtitle(self, video_path: Path, subtitle_index: int, output_format: str = 'srt') -> Optional[Path]:
        """Extract subtitle track from video file."""
        # Ensure output_format has a dot prefix for comparison
        if not output_format.startswith('.'):
            output_format = '.' + output_format
            
        if output_format not in SUPPORTED_SUBTITLE_FORMATS:
            raise ValueError(f"Unsupported subtitle format: {output_format}")
        
        # Create output filename (remove dot for filename)
        video_name = video_path.stem
        output_filename = f"{video_name}_subtitle_{subtitle_index}{output_format}"
        
        # Output to subtitles directory, not the input directory
        output_path = self.subtitles_dir / output_filename
        
        try:
            # Extract subtitle using FFmpeg
            # Use the correct subtitle stream mapping - try different approaches
            stream = ffmpeg.input(str(video_path))
            
            # First try the direct stream mapping
            try:
                output_stream = ffmpeg.output(stream, str(output_path), 
                                           map=f"0:{subtitle_index}",
                                           f=output_format.replace('.', ''),  # Remove dot for FFmpeg format
                                           acodec='none',  # No audio
                                           vcodec='none')  # No video
                
                # Run FFmpeg
                result = ffmpeg.run(output_stream, overwrite_output=True, quiet=False, capture_stdout=True, capture_stderr=True)
                
            except ffmpeg.Error:
                # If direct mapping fails, try using the subtitle stream mapping
                print(f"  Retrying with subtitle stream mapping...")
                output_stream = ffmpeg.output(stream, str(output_path), 
                                           map=f"0:s:{subtitle_index}",
                                           f=output_format.replace('.', ''),  # Remove dot for FFmpeg format
                                           acodec='none',  # No audio
                                           vcodec='none')  # No video
                
                # Run FFmpeg
                result = ffmpeg.run(output_stream, overwrite_output=True, quiet=False, capture_stdout=True, capture_stderr=True)
            
            # Result is already captured from the try/except blocks above
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"Successfully extracted subtitle: {output_filename}")
                return output_path
            else:
                print(f"Failed to extract subtitle: {output_filename}")
                print(f"FFmpeg output: {result}")
                return None
                
        except ffmpeg.Error as e:
            print(f"Error extracting subtitle from {video_path}: {e}")
            if hasattr(e, 'stderr'):
                print(f"FFmpeg stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
            return None
    
    def extract_all_subtitles(self, video_path: Path) -> List[Path]:
        """Extract all available subtitle tracks from a video file."""
        subtitle_tracks = self.list_subtitle_tracks(video_path)
        extracted_files = []
        
        if not subtitle_tracks:
            print(f"No subtitle tracks found in {video_path}")
            return extracted_files
        
        print(f"Found {len(subtitle_tracks)} subtitle track(s) in {video_path.name}")
        
        for track in subtitle_tracks:
            print(f"Extracting track {track['index']} ({track['language']}): {track['title']}")
            extracted_file = self.extract_subtitle(video_path, track['index'])
            if extracted_file:
                extracted_files.append(extracted_file)
        
        return extracted_files
    
    def set_input_directory(self, input_dir: Path):
        """Set the input directory for video processing."""
        self.base_videos_dir = input_dir
    
    def find_video_files(self, input_dir: Path = None) -> List[Path]:
        """Find all video files in the specified input directory."""
        video_files = []
        
        # Use provided input_dir or fall back to default
        search_dir = input_dir or self.base_videos_dir
        
        if not search_dir.exists():
            print(f"Base videos directory not found: {self.base_videos_dir}")
            return video_files
        
        for file_path in self.base_videos_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS:
                video_files.append(file_path)
        
        return sorted(video_files)
    
    def process_all_videos(self) -> Dict[Path, List[Path]]:
        """Process all videos in the base_videos directory and extract subtitles."""
        video_files = self.find_video_files()
        results = {}
        
        if not video_files:
            print("No video files found in base_videos directory")
            return results
        
        print(f"Found {len(video_files)} video file(s)")
        
        for video_path in video_files:
            print(f"\nProcessing: {video_path.name}")
            extracted_subtitles = self.extract_all_subtitles(video_path)
            results[video_path] = extracted_subtitles
        
        return results


def main():
    """Main function for testing subtitle extraction."""
    extractor = SubtitleExtractor()
    
    # List all video files
    video_files = extractor.find_video_files()
    print(f"Found {len(video_files)} video file(s):")
    for video in video_files:
        print(f"  - {video.name}")
    
    # Process first video as example
    if video_files:
        print(f"\nProcessing first video: {video_files[0].name}")
        subtitle_tracks = extractor.list_subtitle_tracks(video_files[0])
        print(f"Subtitle tracks: {subtitle_tracks}")
        
        if subtitle_tracks:
            extractor.extract_subtitle(video_files[0], subtitle_tracks[0]['index'])


if __name__ == "__main__":
    main()
