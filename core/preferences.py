"""User preferences and settings management."""
import json
import os
from typing import Optional, List, Any


class Preferences:
    """Manages application preferences and settings."""
    
    DEFAULT_PREFS = {
        'main_character': None,
        'main_character_path': None,
        'rank_badge_path': None,
        'alt_characters': ['Dhalsim', 'Elena', 'Cammy'],
        'dark_mode': False,
        'active_db_path': None,
        'character_name_override': None,
        'rename_character': None  # NEW: Character to use for file renaming
    }
    
    def __init__(self, prefs_file: str):
        self.prefs_file = prefs_file
        self.data = self.DEFAULT_PREFS.copy()
        self.load()
    
    def load(self):
        """Load preferences from file."""
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Failed to load preferences: {e}")
    
    def save(self):
        """Save preferences to file."""
        try:
            os.makedirs(os.path.dirname(self.prefs_file), exist_ok=True)
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Failed to save preferences: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a preference value and save."""
        self.data[key] = value
        self.save()
    
    def get_main_character(self) -> Optional[str]:
        """Get main character name."""
        return self.data.get('character_name_override') or self.data.get('main_character')
    
    def set_main_character(self, name: str, portrait_path: Optional[str] = None):
        """Set main character."""
        self.data['main_character'] = name
        if portrait_path:
            self.data['main_character_path'] = portrait_path
        self.save()
    
    def get_alt_characters(self) -> List[str]:
        """Get list of alt characters."""
        return self.data.get('alt_characters', [])
    
    def set_alt_characters(self, characters: List[str]):
        """Set alt characters."""
        self.data['alt_characters'] = characters
        self.save()
    
    def get_rename_character(self) -> Optional[str]:
        """Get the character name to use for file renaming."""
        return self.data.get('rename_character')
    
    def set_rename_character(self, character: Optional[str]):
        """Set the character name to use for file renaming."""
        self.data['rename_character'] = character
        self.save()