# Installation Checklist

Follow this checklist to ensure everything is properly set up before running the application.

## ✅ Prerequisites

- [ ] **Python 3.8+** installed and accessible from command line
- [ ] **FFmpeg** installed and added to system PATH
- [ ] **Git** (optional, for cloning the repository)

## ✅ FFmpeg Installation

### Windows
- [ ] Downloaded FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- [ ] Extracted to a folder (e.g., `C:\ffmpeg`)
- [ ] Added `C:\ffmpeg\bin` to system PATH
- [ ] Restarted command prompt/terminal
- [ ] Verified with `ffmpeg -version`

### Alternative Windows Methods
- [ ] **Chocolatey**: `choco install ffmpeg`
- [ ] **Scoop**: `scoop install ffmpeg`
- [ ] **Winget**: `winget install ffmpeg`

### macOS
- [ ] **Homebrew**: `brew install ffmpeg`
- [ ] **MacPorts**: `sudo port install ffmpeg`

### Linux
- [ ] **Ubuntu/Debian**: `sudo apt install ffmpeg`
- [ ] **CentOS/RHEL/Fedora**: `sudo yum install ffmpeg` or `sudo dnf install ffmpeg`
- [ ] **Arch**: `sudo pacman -S ffmpeg`

## ✅ Repository Setup

- [ ] Cloned or downloaded the repository
- [ ] Navigated to the project directory
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated virtual environment:
  - Windows: `venv\Scripts\activate`
  - macOS/Linux: `source venv/bin/activate`

## ✅ Python Dependencies

- [ ] Installed requirements: `pip install -r requirements.txt`
- [ ] Verified no installation errors

## ✅ Configuration

- [ ] Copied `env.example` to `.env`
- [ ] Added LARA MCP Server credentials to `.env`:
  - `LARA_ACCESS_KEY_ID=your_key_here`
  - `LARA_ACCESS_KEY_SECRET=your_secret_here`
- [ ] Verified `.env` file is in project root

## ✅ Testing

- [ ] Tested FFmpeg: `ffmpeg -version`
- [ ] Tested Python: `python --version`
- [ ] Tested MCP connection: `python main.py --test`

## ✅ Ready to Run

- [ ] **GUI**: `python gui.py` or `launch_gui.bat`
- [ ] **CLI**: `python main.py --help` or `run.bat`

## 🚨 Common Issues

### FFmpeg Not Found
- Ensure the `bin` folder (not the main folder) is in PATH
- Restart terminal after adding to PATH
- Check if FFmpeg is actually installed

### Python Import Errors
- Ensure virtual environment is activated
- Verify all requirements are installed
- Check Python version compatibility

### LARA Connection Failed
- Verify `.env` file exists and has correct credentials
- Check internet connection
- Verify LARA service is available

## 📁 Directory Structure

Ensure these directories exist (they should be created automatically):
- `base_videos/` - Place your input videos here
- `output/` - Processed videos will appear here
- `subtitles/` - Extracted subtitle files
- `translated_subtitles/` - Translated subtitle files

## 🎯 Next Steps

After completing the checklist:
1. Place some video files in `base_videos/`
2. Run the GUI: `python gui.py`
3. Select input and output folders
4. Start processing your videos!

## 📞 Need Help?

- Check the main README.md for detailed instructions
- Review PROJECT_STRUCTURE.md for file organization
- Check the troubleshooting section in README.md
