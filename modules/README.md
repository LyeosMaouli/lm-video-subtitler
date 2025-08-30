# Modules

This folder contains the core modules for the Video Subtitle Processor project.

## Available Modules

### `core_processor.py`
Core video processing logic separated from the GUI.
- **CoreProcessor**: Main processing class that handles video operations
- **Queue management**: Thread-safe queue operations
- **Processing methods**: Extract, merge, and process all operations
- **Translation testing**: Integration with LARA translation service

### `settings_manager.py`
Settings management and configuration persistence.
- **SettingsManager**: Handles application configuration
- **JSON persistence**: Saves/loads user preferences
- **Recent folders**: Tracks recently used input/output folders
- **Translation settings**: Manages language preferences

### `ui_components.py`
Reusable UI components for the GUI.
- **FolderSelectionFrame**: Input/output folder selection
- **QueueFrame**: Processing queue management
- **ControlFrame**: Processing control buttons
- **TranslationFrame**: Translation testing interface
- **StatusFrame**: Status display and progress bar
- **SubtitleSelectionDialog**: Subtitle file selection dialog

## Module Dependencies

```
core_processor.py
├── config.py
├── subtitle_extractor.py
├── translator.py
└── video_processor.py

settings_manager.py
└── (no external dependencies)

ui_components.py
└── tkinter (built-in)
```

## Adding New Modules

When adding new modules:
1. Place them in this `modules/` folder
2. Update this README with documentation
3. Ensure proper import statements
4. Follow the established coding patterns
5. Add type hints and docstrings
