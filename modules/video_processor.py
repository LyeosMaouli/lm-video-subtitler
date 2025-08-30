"""
Video processing module for incorporating translated subtitles.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import ffmpeg
import os
from config import OUTPUT_DIR, FFMPEG_CRF, FFMPEG_PRESET, FFMPEG_PATH


class VideoProcessor:
    """Handles video processing and subtitle incorporation."""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR  # Default fallback
        
        # Configure FFmpeg path by adding to PATH
        if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
            # Check if both executables exist
            ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
            ffprobe_exe = os.path.join(FFMPEG_PATH, "ffprobe.exe")
            
            if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
                if FFMPEG_PATH not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ.get('PATH', '')
                # Only print once per class instance
                print(f"✅ VideoProcessor: FFmpeg configured")
            else:
                print(f"⚠️  VideoProcessor: Missing FFmpeg executables in {FFMPEG_PATH}")
        else:
            print(f"⚠️  VideoProcessor: FFmpeg directory not found at {FFMPEG_PATH}")
    
    def set_output_directory(self, output_dir: Path):
        """Set the output directory for video processing."""
        self.output_dir = output_dir
    
    def incorporate_subtitle(self, video_path: Path, subtitle_path: Path, 
                           output_path: Path = None, language_code: str = 'fra') -> Optional[Path]:
        """Incorporate subtitle file into video."""
        if not video_path.exists():
            print(f"Video file not found: {video_path}")
            return None
        
        if not subtitle_path.exists():
            print(f"Subtitle file not found: {subtitle_path}")
            return None
        
        # Create output filename
        if output_path is None:
            video_name = video_path.stem
            subtitle_name = subtitle_path.stem
            output_filename = f"{video_name}_with_{subtitle_name}.mkv"
            output_path = self.output_dir / output_filename
        
        try:
            print(f"Processing video: {video_path.name}")
            print(f"Adding subtitle: {subtitle_path.name}")
            
            # Get video info
            video_info = self._get_video_info(video_path)
            if not video_info:
                return None
            
            # Create FFmpeg command to add subtitle
            stream = ffmpeg.input(str(video_path))
            
            # Add subtitle stream
            subtitle_stream = ffmpeg.input(str(subtitle_path))
            
            # Output with subtitle
            stream = ffmpeg.output(
                stream, 
                subtitle_stream,
                str(output_path),
                vcodec='copy',  # Copy video codec
                acodec='copy',  # Copy audio codec
                scodec='copy',  # Copy subtitle codec
                metadata=f"language={language_code}",
                f='matroska'  # Force MKV output format
            )
            
            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=False)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"Successfully created video with subtitle: {output_path.name}")
                return output_path
            else:
                print(f"Failed to create video with subtitle: {output_path.name}")
                return None
                
        except ffmpeg.Error as e:
            print(f"Error processing video {video_path}: {e}")
            return None
    
    def create_hardcoded_subtitle_video(self, video_path: Path, subtitle_path: Path,
                                      output_path: Path = None, language_code: str = 'fra') -> Optional[Path]:
        """Create video with hardcoded (burned-in) subtitles."""
        if not video_path.exists():
            print(f"Video file not found: {video_path}")
            return None
        
        if not subtitle_path.exists():
            print(f"Subtitle file not found: {subtitle_path}")
            return None
        
        # Create output filename
        if output_path is None:
            video_name = video_path.stem
            subtitle_name = subtitle_path.stem
            output_filename = f"{video_name}_hardcoded_{subtitle_name}.mkv"
            output_path = self.output_dir / output_filename
        
        try:
            print(f"Creating hardcoded subtitle video: {video_path.name}")
            print(f"Using subtitle: {subtitle_path.name}")
            
            # Create FFmpeg command for hardcoded subtitles
            stream = ffmpeg.input(str(video_path))
            
            # Add subtitle filter
            stream = ffmpeg.filter(stream, 'subtitles', str(subtitle_path))
            
            # Output with hardcoded subtitle
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264',  # Re-encode video for subtitle burning
                acodec='copy',     # Copy audio codec
                crf=FFMPEG_CRF,    # Video quality
                preset=FFMPEG_PRESET,  # Encoding preset
                f='matroska'
            )
            
            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=False)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"Successfully created hardcoded subtitle video: {output_path.name}")
                return output_path
            else:
                print(f"Failed to create hardcoded subtitle video: {output_path.name}")
                return None
                
        except ffmpeg.Error as e:
            print(f"Error creating hardcoded subtitle video {video_path}: {e}")
            return None
    
    def _get_video_info(self, video_path: Path) -> Optional[Dict]:
        """Get information about a video file."""
        try:
            probe = ffmpeg.probe(str(video_path))
            return probe
        except ffmpeg.Error as e:
            print(f"Error probing video {video_path}: {e}")
            return None
    
    def process_video_with_subtitle(self, video_path: Path, subtitle_path: Path,
                                  hardcoded: bool = False, language_code: str = 'fra') -> Optional[Path]:
        """Process video with subtitle (either embedded or hardcoded)."""
        if hardcoded:
            return self.create_hardcoded_subtitle_video(video_path, subtitle_path, language_code=language_code)
        else:
            return self.incorporate_subtitle(video_path, subtitle_path, language_code=language_code)
    
    def batch_process_videos(self, video_subtitle_pairs: List[tuple], 
                           hardcoded: bool = False, language_code: str = 'fra') -> List[Path]:
        """Process multiple videos with their corresponding subtitle files."""
        results = []
        
        for video_path, subtitle_path in video_subtitle_pairs:
            print(f"\nProcessing: {video_path.name}")
            result = self.process_video_with_subtitle(
                video_path, subtitle_path, hardcoded, language_code
            )
            if result:
                results.append(result)
        
        return results
    
    def create_video_without_subtitles(self, video_path: Path, output_path: Path = None) -> Optional[Path]:
        """Create a video file without any subtitle tracks."""
        if not video_path.exists():
            print(f"Video file not found: {video_path}")
            return None
        
        # Create output filename
        if output_path is None:
            video_name = video_path.stem
            output_filename = f"{video_name}_no_subtitles.mkv"
            output_path = self.output_dir / output_filename
        
        try:
            print(f"Creating video without subtitles: {video_path.name}")
            
            # Create FFmpeg command to copy video and audio without subtitles
            stream = ffmpeg.input(str(video_path))
            
            # Output without subtitle streams - use direct subprocess call to FFmpeg
            # This approach gives us full control over FFmpeg command-line arguments
            try:
                import subprocess
                
                # Build FFmpeg command directly
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-map', '0:v',  # Map video stream
                    '-map', '0:a',  # Map audio stream
                    '-c:v', 'copy',  # Copy video codec
                    '-c:a', 'copy',  # Copy audio codec
                    '-f', 'matroska',  # Force MKV output format
                    '-y',  # Overwrite output
                    str(output_path)
                ]
                
                print(f"Executing FFmpeg command: {' '.join(cmd)}")
                
                # Run FFmpeg command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"FFmpeg command executed successfully")
                
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg command failed: {e}")
                print(f"FFmpeg stderr: {e.stderr}")
                raise ffmpeg.Error(f"FFmpeg command failed: {e}")
            except Exception as e:
                print(f"Direct FFmpeg approach failed: {e}")
                # Fallback: use ffmpeg-python without map options (will include subtitles)
                print("Falling back to ffmpeg-python approach (may include subtitles)")
                output_stream = ffmpeg.output(
                    stream,
                    str(output_path),
                    vcodec='copy',  # Copy video codec
                    acodec='copy',  # Copy audio codec
                    f='matroska'    # Force MKV output format
                )
                ffmpeg.run(output_stream, overwrite_output=True, quiet=False)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"Successfully created video without subtitles: {output_path.name}")
                return output_path
            else:
                print(f"Failed to create video without subtitles: {output_path.name}")
                return None
                
        except ffmpeg.Error as e:
            print(f"Error creating video without subtitles {video_path}: {e}")
            return None
    
    def cleanup_temp_files(self, temp_files: List[Path]):
        """Clean up temporary files."""
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    print(f"Cleaned up: {temp_file.name}")
            except Exception as e:
                print(f"Error cleaning up {temp_file}: {e}")


def main():
    """Main function for testing video processing."""
    processor = VideoProcessor()
    
    # Test video info
    video_files = list(Path("base_videos").glob("*.mkv"))
    if video_files:
        video_path = video_files[0]
        print(f"Testing with video: {video_path.name}")
        
        info = processor._get_video_info(video_path)
        if info:
            print("Video info retrieved successfully")
            print(f"Duration: {info.get('format', {}).get('duration', 'Unknown')} seconds")
            print(f"Size: {info.get('format', {}).get('size', 'Unknown')} bytes")
        else:
            print("Failed to get video info")


if __name__ == "__main__":
    main()
