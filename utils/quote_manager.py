"""Character quote loading and management."""
import json
import random
from typing import Dict, List, Optional
import os


class QuoteManager:
    """Manages character quotes."""
    
    def __init__(self, quotes_json_path: str):
        self.quotes_path = quotes_json_path
        self.quotes: Dict[str, List[str]] = {}
        self.load_quotes()
    
    def load_quotes(self):
        """Load quotes from JSON file."""
        if not os.path.exists(self.quotes_path):
            print(f"Quotes file not found: {self.quotes_path}")
            return
            
        try:
            with open(self.quotes_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            
            if isinstance(raw, dict):
                for char, quote_list in raw.items():
                    if isinstance(quote_list, list):
                        cleaned = [str(q).strip() for q in quote_list if str(q).strip()]
                        if cleaned:
                            self.quotes[str(char).strip()] = cleaned
        except Exception as e:
            print(f"Failed to load quotes: {e}")
    
    def get_random_quote(self, character: str) -> str:
        """Get a random quote for a character."""
        # Try exact match first
        if character in self.quotes:
            return random.choice(self.quotes[character])
        
        # Try case-insensitive match
        char_lower = character.lower()
        for key, quotes in self.quotes.items():
            if key.lower() == char_lower:
                return random.choice(quotes)
        
        return "No quotes available"
    
    def has_quotes(self, character: str) -> bool:
        """Check if character has quotes."""
        return character in self.quotes or \
               any(k.lower() == character.lower() for k in self.quotes.keys())