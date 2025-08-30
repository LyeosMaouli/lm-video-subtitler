# Tools

This folder contains utility scripts for the Video Subtitle Processor project.

## Available Tools

### `rename_videos.py`
A utility script to rename video files by removing specific suffixes from filenames.

**Usage:**
```bash
python tools/rename_videos.py
```

**What it does:**
- Removes the suffix "1080p.BILI.WEB-DL.ZHO.AAC2.0.H.265.MSubs-ToonsHub" from video filenames
- Makes filenames cleaner and more manageable
- Example: `Psychic.Princess.S02E01.1080p.BILI.WEB-DL.ZHO.AAC2.0.H.265.MSubs-ToonsHub.mkv` → `Psychic.Princess.S02E01.mkv`

## Adding New Tools

When adding new utility scripts:
1. Place them in this `tools/` folder
2. Update this README with documentation
3. Ensure scripts are executable and well-documented
4. Consider adding command-line arguments for flexibility
