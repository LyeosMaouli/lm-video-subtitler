# Project Structure - Organized Python Files

## Root Directory Structure

The Python files have been properly organized for better maintainability and structure.

### Root Directory (Main Applications)
```
📁 lm-video-subtitler/
├── 🐍 main.py                    # CLI main application
├── 🐍 gui.py                     # GUI main application  
├── 🐍 config.py                  # Configuration settings
├── 📄 requirements.txt           # Python dependencies
├── 📄 env.example               # Environment variables template
├── 📄 README.md                 # Project documentation
├── 📄 .gitignore                # Git ignore rules
├── 🚀 launch_gui.bat            # Windows GUI launcher
└── 🚀 run.bat                   # Windows CLI launcher
```

### Modules Directory (Core Logic)
```
📁 modules/
├── 🐍 __init__.py               # Makes modules a Python package
├── 🐍 core_processor.py         # Core video processing logic
├── 🐍 settings_manager.py       # Application settings management
├── 🐍 ui_components.py          # Reusable Tkinter UI components
├── 🐍 subtitle_extractor.py     # Subtitle extraction functionality
├── 🐍 translator.py             # LARA MCP translation module
├── 🐍 video_processor.py        # Video processing operations
└── 📄 README.md                 # Modules documentation
```

### Tools Directory (Utility Scripts)
```
📁 tools/
├── 🐍 __init__.py               # Makes tools a Python package
├── 🐍 rename_videos.py          # Video file renaming utility
└── 📄 README.md                 # Tools documentation
```

### Documentation Directory
```
📁 docs/
├── 📄 fix_plan.md               # Code review and fix plan
├── 📄 fixes_applied.md          # Summary of applied fixes
└── 📄 project_structure.md      # This file
```

## File Organization Principles

### ✅ **Root Directory**
- **Main applications**: `main.py`, `gui.py`
- **Configuration**: `config.py`
- **Project metadata**: `requirements.txt`, `README.md`, `.gitignore`
- **Launchers**: Batch files for Windows users

### ✅ **Modules Directory**
- **Core business logic**: All processing, translation, and video operations
- **UI components**: Reusable Tkinter widgets
- **Settings management**: Application configuration persistence

### ✅ **Tools Directory**
- **Utility scripts**: One-off tools and maintenance scripts
- **Standalone functionality**: Scripts that can run independently

## Import Structure

### From Root
```python
# Main applications can import from modules
from modules.subtitle_extractor import SubtitleExtractor
from modules.translator import LARATranslator
from modules.video_processor import VideoProcessor
```

### From Modules
```python
# Module files use relative imports
from .subtitle_extractor import SubtitleExtractor
from .translator import LARATranslator
from .video_processor import VideoProcessor
```

## Benefits of This Organization

1. **Clear Separation**: Main apps vs. core logic vs. utilities
2. **Better Maintainability**: Related functionality grouped together
3. **Easier Testing**: Modules can be tested independently
4. **Cleaner Imports**: Clear import paths and dependencies
5. **Scalability**: Easy to add new modules or tools
6. **Professional Structure**: Follows Python project best practices

## File Dependencies

```
main.py → modules/*.py → config.py
gui.py → modules/*.py → config.py
modules/core_processor.py → modules/*.py → config.py
```

## Next Steps

1. **Test the organization**: Ensure all imports work correctly
2. **Update documentation**: Reflect new structure in README
3. **Consider packaging**: Could be packaged as a proper Python package
4. **Add tests**: Create test directory for unit tests
