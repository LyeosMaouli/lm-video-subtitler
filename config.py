"""
Configuration file for the video subtitle extractor and translator.
"""
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(".env file loaded successfully")
except ImportError:
    print("! python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"! Error loading .env file: {e}")

# Project paths
PROJECT_ROOT = Path(__file__).parent
BASE_VIDEOS_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
SUBTITLES_DIR = PROJECT_ROOT / "subtitles"
TRANSLATED_SUBTITLES_DIR = PROJECT_ROOT / "translated_subtitles"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, SUBTITLES_DIR, TRANSLATED_SUBTITLES_DIR]:
    directory.mkdir(exist_ok=True)

# LARA MCP Server configuration
MCP_SERVER_URL = os.getenv("LARA_MCP_SERVER_URL", "https://mcp.laratranslate.com/v1")
LARA_ACCESS_KEY_ID = os.getenv("LARA_ACCESS_KEY_ID", "")
LARA_ACCESS_KEY_SECRET = os.getenv("LARA_ACCESS_KEY_SECRET", "")

# Translation settings
SOURCE_LANGUAGE = "en"  # English
TARGET_LANGUAGE = "fr"  # French

# Video processing settings
SUPPORTED_VIDEO_FORMATS = [".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]
SUPPORTED_SUBTITLE_FORMATS = [".srt", ".ass", ".ssa", ".sub", ".vtt"]

# FFmpeg settings
FFMPEG_CRF = 23  # Constant Rate Factor for video quality
FFMPEG_PRESET = "medium"  # Encoding preset (fast, medium, slow)
FFMPEG_PATH = "C:\\ffmpeg\\bin"  # Path to FFmpeg directory containing ffmpeg.exe and ffprobe.exe

# Subtitle extraction settings
MIN_SUBTITLE_DURATION = 0.5  # Minimum subtitle duration in seconds
MAX_SUBTITLE_DURATION = 10.0  # Maximum subtitle duration in seconds
