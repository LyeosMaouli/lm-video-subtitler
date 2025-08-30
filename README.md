# Video Subtitle Extractor and Translator

A Python application that extracts subtitles from video files (MKV, MP4, etc.), translates them from English to French using the LARA MCP Server, and incorporates the translated subtitles back into the video files.

## Features

- **Subtitle Extraction**: Extract subtitle tracks from various video formats using FFmpeg
- **Translation**: Translate subtitles from English to French using LARA MCP Server
- **Video Processing**: Incorporate translated subtitles back into videos (embedded or hardcoded)
- **Batch Processing**: Process multiple videos automatically
- **Multiple Output Formats**: Support for both embedded and hardcoded subtitle videos
- **Graphical User Interface**: Easy-to-use GUI for managing video processing

## Requirements

### System Requirements
- **FFmpeg**: Must be installed and available in your system PATH
- **Python 3.8+**: For running the application
- **Windows 10/11**: Tested on Windows, but should work on other platforms

### FFmpeg Installation (Windows)

**Option 1: Download and Install Manually**
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the ZIP file to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH environment variable:
   - Open System Properties → Advanced → Environment Variables
   - Edit the PATH variable and add `C:\ffmpeg\bin`
4. Restart your command prompt/terminal
5. Verify installation by running `ffmpeg -version`

**Option 2: Using Chocolatey (Recommended)**
```cmd
choco install ffmpeg
```

**Option 3: Using Scoop**
```cmd
scoop install ffmpeg
```

**Option 4: Using Winget**
```cmd
winget install ffmpeg
```

### FFmpeg Installation (macOS)
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

### FFmpeg Installation (Linux)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo yum install ffmpeg
# or
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd lm-video-subtitler
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   copy env.example .env
   
   # Edit .env with your LARA MCP Server details
   notepad .env
   ```

## Configuration

### Environment Variables (.env file)

Create a `.env` file in the project root with the following variables:

```env
# LARA MCP Server Configuration
LARA_MCP_SERVER_URL=https://mcp.laratranslate.com/v1
LARA_ACCESS_KEY_ID=your_access_key_id_here
LARA_ACCESS_KEY_SECRET=your_access_key_secret_here

# Optional: Override default language settings
# SOURCE_LANGUAGE=en
# TARGET_LANGUAGE=fr
```

### LARA MCP Server Setup

1. **Get your LARA access credentials** from your LARA account
2. **Set the server URL** in your `.env` file (default: https://mcp.laratranslate.com/v1)
3. **Configure your access key ID and secret** in the `.env` file
4. **Test connection** using the `--test` flag

## Usage

### GUI Application (Recommended)

For the easiest experience, use the graphical user interface:

```bash
# Windows
launch_gui.bat

# Or directly with Python
python gui.py
```

The GUI provides:
- **Folder Selection**: Choose input and output directories
- **Queue Management**: View and manage video processing queue
- **Subtitle Selection**: Double-click queue items to select subtitles
- **Processing Controls**: Extract, merge, or process all videos
- **Translation Testing**: Test LARA translation without processing videos
- **Real-time Status**: Monitor progress and view detailed logs

### Command Line Interface

For advanced users or automation:

1. **Test MCP server connection**
   ```bash
   python main.py --test
   ```

2. **Process a single video**
   ```bash
   python main.py --video "base_videos/your_video.mkv"
   ```

3. **Process all videos in base_videos directory**
   ```bash
   python main.py --all
   ```

4. **Create hardcoded subtitle videos**
   ```bash
   python main.py --all --hardcoded
   ```

5. **Keep intermediate subtitle files**
   ```bash
   python main.py --all --keep-files
   ```

### Command Line Options

- `--video, -v`: Process specific video file
- `--all, -a`: Process all videos in base_videos directory
- `--hardcoded, -h`: Create hardcoded subtitle videos (burned-in)
- `--keep-files, -k`: Keep intermediate subtitle files for inspection
- `--test, -t`: Test MCP server connection
- `--help`: Show help information

### Workflow

The application follows this workflow for each video:

1. **Extract Subtitles**: Uses FFmpeg to extract all subtitle tracks
2. **Translate Subtitles**: Sends subtitle text to LARA MCP Server for translation
3. **Process Video**: Incorporates translated subtitles back into the video
4. **Output**: Saves processed video to the `output/` directory

## Project Structure

```
lm-video-subtitler/
├── base_videos/              # Input video files
├── output/                   # Processed videos with translated subtitles
├── subtitles/                # Extracted subtitle files (temporary)
├── translated_subtitles/     # Translated subtitle files (temporary)
├── modules/                  # Core application modules
│   ├── __init__.py
│   ├── core_processor.py     # Core video processing logic
│   ├── mcp_client.py         # LARA MCP Server communication
│   ├── subtitle_extractor.py # Subtitle extraction using FFmpeg
│   ├── video_processor.py    # Video processing and subtitle incorporation
│   └── ui_components.py      # Reusable GUI components
├── tools/                    # Utility scripts
│   ├── __init__.py
│   └── rename_videos.py      # Video filename cleanup utility
├── docs/                     # Documentation
├── config.py                 # Configuration and constants
├── main.py                   # Main application and CLI interface
├── gui.py                    # Graphical user interface
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── launch_gui.bat           # Windows GUI launcher
├── run.bat                  # Windows CLI launcher
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Output Files

- **Embedded Subtitles**: Videos with selectable subtitle tracks
- **Hardcoded Subtitles**: Videos with permanently burned-in subtitles
- **File Naming**: `{original_name}_with_{subtitle_name}.mkv` or `{original_name}_hardcoded_{subtitle_name}.mkv`

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in your system PATH
   - Test with `ffmpeg -version` in command prompt
   - On Windows, make sure you've added the `bin` folder to PATH, not the main folder
   - Restart your terminal/command prompt after adding to PATH

2. **LARA MCP Server connection failed**
   - Check your `.env` file configuration
   - Verify your LARA access credentials are correct
   - Test connection with `python main.py --test`

3. **No subtitles found**
   - Verify the video file contains subtitle tracks
   - Check if subtitles are embedded or external
   - Use `ffprobe` to inspect video file structure

4. **Translation failures**
   - Check LARA MCP server logs for errors
   - Verify access key ID and secret are correct
   - Test with simple text first

### Debug Mode

For detailed error information, you can modify the code to enable debug logging or run individual modules:

```bash
# Test subtitle extraction
python -c "from modules.subtitle_extractor import SubtitleExtractor; print('Subtitle extractor loaded successfully')"

# Test translation
python -c "from modules.mcp_client import MCPClient; print('MCP client loaded successfully')"

# Test video processing
python -c "from modules.video_processor import VideoProcessor; print('Video processor loaded successfully')"
```

## Performance Considerations

- **Large Videos**: Processing large video files can take significant time
- **Batch Processing**: Use `--all` flag for multiple videos
- **Hardcoded Subtitles**: Re-encoding takes longer but provides universal compatibility
- **Memory Usage**: Large subtitle files may require more memory during translation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **FFmpeg**: For video processing capabilities
- **LARA MCP Server**: For translation services
- **Python Community**: For the excellent libraries used in this project
