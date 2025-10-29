"""Database operations for replay management."""
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


class ReplayDatabase:
    """Handles all database operations for replay management."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database with required tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Main replays table
            c.execute('''
                CREATE TABLE IF NOT EXISTS replays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_link TEXT,
                    file_name TEXT,
                    timestamp TEXT,
                    ufc TEXT UNIQUE,
                    extended_desc TEXT,
                    recorded INTEGER,
                    renamed_filename TEXT,
                    date_added TEXT,
                    tags TEXT
                )
            ''')
            
            # Recycle bin table
            c.execute('''
                CREATE TABLE IF NOT EXISTS recycle_bin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_link TEXT,
                    file_name TEXT,
                    timestamp TEXT,
                    ufc TEXT UNIQUE,
                    extended_desc TEXT,
                    recorded INTEGER,
                    renamed_filename TEXT,
                    date_added TEXT,
                    deleted_date TEXT,
                    tags TEXT
                )
            ''')
            
            # Database info table
            c.execute('''
                CREATE TABLE IF NOT EXISTS db_info (
                    unique_db_code TEXT UNIQUE
                )
            ''')
            
            conn.commit()
    
    def add_replay(self, file_name: str, timestamp: str = "", 
                   video_link: str = "", description: str = "",
                   tags: str = "") -> str:
        """Add a new replay entry."""
        ufc = self._generate_ufc(file_name)
        date_added = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO replays (video_link, file_name, timestamp, ufc, 
                                   extended_desc, recorded, date_added, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (video_link, file_name, timestamp, ufc, description, 0, date_added, tags))
            conn.commit()
        
        return ufc
    
    def get_all_replays(self) -> List[Dict]:
        """Retrieve all replays from the database."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT file_name, timestamp, ufc, recorded, video_link, 
                       extended_desc, date_added, tags
                FROM replays
            ''')
            rows = c.fetchall()
        
        replays = []
        for row in rows:
            replays.append({
                'file_name': row[0] or "",
                'timestamp': row[1] or "",
                'ufc': row[2] or "",
                'recorded': bool(row[3]),
                'video_link': row[4] or "",
                'description': row[5] or "",
                'date_added': row[6] or "",
                'tags': row[7] or ""
            })
        
        return replays
    
    def update_replay(self, ufc: str, **kwargs):
        """Update a replay entry."""
        valid_fields = ['file_name', 'timestamp', 'video_link', 
                       'extended_desc', 'recorded', 'tags']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return
        
        values.append(ufc)
        query = f"UPDATE replays SET {', '.join(updates)} WHERE ufc = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(query, values)
            conn.commit()
    
    def delete_replay(self, ufc: str, permanent: bool = False):
        """Delete a replay (to recycle bin or permanently)."""
        if permanent:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM replays WHERE ufc = ?", (ufc,))
                conn.commit()
        else:
            # Move to recycle bin
            self._move_to_recycle_bin(ufc)
    
    def _move_to_recycle_bin(self, ufc: str):
        """Move a replay to the recycle bin."""
        deleted_date = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Get replay data
            c.execute('''
                SELECT video_link, file_name, timestamp, ufc, extended_desc,
                       recorded, renamed_filename, date_added, tags
                FROM replays WHERE ufc = ?
            ''', (ufc,))
            
            data = c.fetchone()
            if not data:
                return
            
            # Insert into recycle bin
            c.execute('''
                INSERT INTO recycle_bin (video_link, file_name, timestamp, ufc,
                                        extended_desc, recorded, renamed_filename,
                                        date_added, deleted_date, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*data, deleted_date))
            
            # Delete from replays
            c.execute("DELETE FROM replays WHERE ufc = ?", (ufc,))
            conn.commit()
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags from the database."""
        tags = set()
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT tags FROM replays WHERE tags IS NOT NULL AND tags != ''")
            rows = c.fetchall()
        
        for (tag_str,) in rows:
            for tag in tag_str.split(','):
                tag = tag.strip()
                if tag:
                    tags.add(tag)
        
        return sorted(tags)
    
    def auto_cleanup_recycle_bin(self, days: int = 30):
        """Automatically delete old items from recycle bin."""
        threshold = (datetime.now() - timedelta(days=days)).strftime("%m-%d-%Y %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM recycle_bin WHERE deleted_date < ?", (threshold,))
            conn.commit()
    
    @staticmethod
    def _generate_ufc(file_name: str) -> str:
        """Generate a unique file code."""
        return f"UFC-{str(uuid.uuid4())[:4].upper()}"