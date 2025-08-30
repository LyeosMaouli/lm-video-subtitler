# Project Structure Overview

This document provides a clear overview of the project's file and directory organization.

## Root Directory Files

### Core Application Files
- **`main.py`** - Main CLI application entry point
- **`gui.py`** - Graphical user interface application
- **`config.py`** - Configuration constants and settings
- **`requirements.txt`** - Python dependencies

### Configuration Files
- **`.env`** - Environment variables (create from `env.example`)
- **`.gitignore`** - Git ignore rules
- **`gui_settings.json`** - GUI application settings

### Launcher Scripts (Windows)
- **`launch_gui.bat`** - Launch the GUI application
- **`run.bat`** - Launch the CLI application

## Directories

### `/base_videos/`
- **Purpose**: Place your input video files here
- **Content**: MKV, MP4, or other video files with embedded subtitles
- **Note**: The application will scan this directory for videos to process

### `/output/`
- **Purpose**: Processed videos are saved here
- **Content**: Videos with translated subtitles (embedded or hardcoded)
- **File Naming**: `{original_name}_with_{subtitle_name}.mkv`

### `/subtitles/`
- **Purpose**: Extracted subtitle files are stored here
- **Content**: SRT files extracted from videos
- **File Naming**: `{video_name}_subtitle_{track_number}_{language}.srt`

### `/translated_subtitles/`
- **Purpose**: Translated subtitle files are stored here
- **Content**: French SRT files translated from English
- **File Naming**: `{video_name}_subtitle_{track_number}_fr.srt`

### `/modules/`
- **Purpose**: Core application modules
- **Content**:
  - `core_processor.py` - Main video processing logic
  - `mcp_client.py` - LARA MCP Server communication
  - `subtitle_extractor.py` - Subtitle extraction using FFmpeg
  - `video_processor.py` - Video processing and subtitle incorporation
  - `ui_components.py` - Reusable GUI components

### `/tools/`
- **Purpose**: Utility scripts and tools
- **Content**:
  - `rename_videos.py` - Clean up video filenames

### `/docs/`
- **Purpose**: Project documentation
- **Content**: Additional documentation files

### `/venv/`
- **Purpose**: Python virtual environment
- **Note**: Created during installation, contains Python packages

### `/merged/`
- **Purpose**: Example output files
- **Content**: Sample processed videos
- **Note**: This directory may contain example outputs for demonstration

## File Flow

```
Input: base_videos/*.mkv
    ↓
Extract: subtitles/*.srt
    ↓
Translate: translated_subtitles/*_fr.srt
    ↓
Process: output/*_with_subtitles.mkv
```

## Getting Started

1. **Place videos** in `/base_videos/`
2. **Configure** your `.env` file
3. **Run the application** using `launch_gui.bat` or `python gui.py`
4. **Select folders** and process your videos
5. **Find results** in `/output/`

## Notes

- The application automatically creates necessary directories
- Temporary files are cleaned up after processing
- Backup files are created during subtitle cleaning operations
- All paths are relative to the project root directory
