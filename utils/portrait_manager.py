"""Portrait image loading and caching."""
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
import os
import re
from typing import Optional, Dict


class PortraitManager:
    """Manages character and rank portrait loading."""
    
    def __init__(self, char_dir: str, rank_dir: str):
        self.char_dir = char_dir
        self.rank_dir = rank_dir
        self._cache: Dict[str, QPixmap] = {}
    
    def load_portrait(self, path: str, size: QSize, 
                     use_cache: bool = True) -> Optional[QPixmap]:
        """Load and scale a portrait image."""
        if not path or not os.path.exists(path):
            return None
        
        cache_key = f"{path}_{size.width()}x{size.height()}"
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return None
        
        scaled = pixmap.scaled(
            size, 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        if use_cache:
            self._cache[cache_key] = scaled
        
        return scaled
    
    def get_character_portraits(self, character_name: str) -> list:
        """Get all portrait files for a character."""
        portraits = []
        
        try:
            if not os.path.exists(self.char_dir):
                return []
                
            for filename in os.listdir(self.char_dir):
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    continue
                
                clean_name = self.clean_filename(filename)
                if character_name.lower() in clean_name.lower():
                    portraits.append(os.path.join(self.char_dir, filename))
        except Exception as e:
            print(f"Error loading portraits: {e}")
        
        return portraits
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Extract clean character name from filename."""
        name, _ = os.path.splitext(filename)
        
        # Remove common suffixes
        for suffix in ["_portrait", "-portrait", "_icon", "-icon", 
                      "_badge", "-badge", "_img", "-img"]:
            if name.lower().endswith(suffix):
                name = name[:-len(suffix)]
        
        # Remove version indicators
        name = re.sub(r'(_|-)(alt|v|ver|version)\d*$', '', name, flags=re.IGNORECASE)
        
        # Clean up separators
        name = name.replace("_", " ").replace("-", " ")
        name = " ".join(name.split())
        
        return name.title()
    
    def clear_cache(self):
        """Clear the portrait cache."""
        self._cache.clear()