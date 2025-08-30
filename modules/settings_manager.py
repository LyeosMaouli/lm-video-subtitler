"""
Settings management for the application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages application settings and configuration."""
    
    def __init__(self, settings_file: str = 'gui_settings.json'):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            'input_folder': '',
            'output_folder': str(Path.cwd() / "output"),
            'window_geometry': '1000x700',
            'last_used_folders': [],
            'recent_outputs': [],
            'translation_settings': {
                'source_language': 'en',
                'target_language': 'fr',
                'test_text': 'Hello, how are you?'
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default settings."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_with_defaults(loaded_settings)
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save current settings to file."""
        try:
            # Ensure output directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _merge_with_defaults(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults to ensure all keys exist."""
        merged = self.default_settings.copy()
        
        def deep_merge(target: Dict, source: Dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(merged, loaded_settings)
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value."""
        keys = key.split('.')
        target = self.settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
        
        # Auto-save on important changes
        if key in ['input_folder', 'output_folder']:
            return self.save_settings()
        
        return True
    
    def add_recent_folder(self, folder_type: str, folder_path: str, max_recent: int = 10):
        """Add a folder to recent folders list."""
        if folder_type == 'input':
            recent_list = self.settings.get('last_used_folders', [])
        elif folder_type == 'output':
            recent_list = self.settings.get('recent_outputs', [])
        else:
            return
        
        # Remove if already exists
        if folder_path in recent_list:
            recent_list.remove(folder_path)
        
        # Add to beginning
        recent_list.insert(0, folder_path)
        
        # Limit list size
        if len(recent_list) > max_recent:
            recent_list = recent_list[:max_recent]
        
        # Update settings
        if folder_type == 'input':
            self.settings['last_used_folders'] = recent_list
        else:
            self.settings['recent_outputs'] = recent_list
        
        self.save_settings()
    
    def get_recent_folders(self, folder_type: str) -> list:
        """Get recent folders list."""
        if folder_type == 'input':
            return self.settings.get('last_used_folders', [])
        elif folder_type == 'output':
            return self.settings.get('recent_outputs', [])
        return []
    
    def update_translation_settings(self, source_lang: str = None, target_lang: str = None, test_text: str = None):
        """Update translation-related settings."""
        if source_lang:
            self.settings['translation_settings']['source_language'] = source_lang
        if target_lang:
            self.settings['translation_settings']['target_language'] = target_lang
        if test_text:
            self.settings['translation_settings']['test_text'] = test_text
        
        self.save_settings()
    
    def get_translation_settings(self) -> Dict[str, str]:
        """Get translation settings."""
        return self.settings.get('translation_settings', {}).copy()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        try:
            self.settings = self.default_settings.copy()
            return self.save_settings()
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False
    
    def export_settings(self, export_path: Path) -> bool:
        """Export settings to a file."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """Import settings from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Merge with current settings
            self.settings = self._merge_with_defaults(imported_settings)
            return self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
