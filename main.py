# ==================== main.py (PROJECT ROOT) ====================
"""
SF6 Replay Knowledge Manager - Main Entry Point
Place this file at: RKM_ver2/main.py
Run with: python main.py
"""
import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SF6 Replay Knowledge Manager")
    app.setOrganizationName("SF6RKM")
    app.setOrganizationDomain("sf6rkm.local")
    
    # Set application icon (optional)
    # icon_path = os.path.join(PROJECT_ROOT, "assets", "app_icon.png")
    # if os.path.exists(icon_path):
    #     app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        print(f"Failed to create main window: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


# ==================== ui/widgets/search_bar.py (COMPLETE) ====================
"""Search bar widget for filtering replays."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal
from typing import Optional


class SearchBar(QWidget):
    """Search bar for filtering replays."""
    
    search_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Search:")
        layout.addWidget(label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by file name, tags, or description...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)
    
    def clear(self):
        """Clear the search input."""
        self.search_input.clear()
    
    def get_text(self) -> str:
        """Get current search text."""
        return self.search_input.text()


# ==================== ui/panels/center_panel.py (COMPLETE) ====================
"""Center panel with alt character rotation."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap
from typing import Optional
import random


class CenterPanel(QWidget):
    """Center panel displaying rotating alt character."""
    
    portrait_update_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.portrait_size = 160
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel("Alt Character: None")
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Portrait
        self.portrait_label = QLabel()
        self.portrait_label.setFixedSize(self.portrait_size, self.portrait_size)
        self.portrait_label.setStyleSheet(
            "border: 2px solid gray; background-color: #1a1a1a;"
        )
        self.portrait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.portrait_label)
        
        # Quote
        self.quote_label = QLabel("No quotes available")
        quote_font = QFont("Arial", 11)
        quote_font.setItalic(True)
        self.quote_label.setFont(quote_font)
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setFixedWidth(self.portrait_size * 2)
        layout.addWidget(self.quote_label)
    
    def setup_timer(self):
        """Setup rotation timer."""
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.portrait_update_requested.emit)
        self.rotation_timer.start(60000)  # 60 seconds
    
    def update_display(self, character: str, pixmap: Optional[QPixmap], quote: str):
        """Update the displayed character, portrait, and quote."""
        self.title_label.setText(f"Alt Character: {character}")
        
        if pixmap:
            self.portrait_label.setPixmap(pixmap)
        else:
            self.portrait_label.clear()
        
        self.quote_label.setText(quote)


# ==================== ui/dialogs/edit_dialog.py (COMPLETE) ====================
"""Edit replay dialog."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from typing import Optional


class EditReplayDialog(QDialog):
    """Dialog for editing an existing replay entry."""
    
    def __init__(self, replay_data: dict, database, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Replay - {replay_data.get('file_name', 'Unknown')}")
        self.resize(500, 400)
        
        self.replay_data = replay_data
        self.database = database
        self.ufc = replay_data.get('ufc', '')
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(f"UFC: {self.ufc}")
        info_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(info_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # File Name
        self.file_name_edit = QLineEdit()
        self.file_name_edit.setText(self.replay_data.get('file_name', ''))
        form_layout.addRow("File Name:", self.file_name_edit)
        
        # Timestamp
        self.timestamp_edit = QLineEdit()
        self.timestamp_edit.setText(self.replay_data.get('timestamp', ''))
        self.timestamp_edit.setPlaceholderText("e.g., 01:23")
        form_layout.addRow("Timestamp:", self.timestamp_edit)
        
        # Video Link
        self.video_link_edit = QLineEdit()
        self.video_link_edit.setText(self.replay_data.get('video_link', ''))
        self.video_link_edit.setPlaceholderText("YouTube URL or file path")
        form_layout.addRow("Video Link:", self.video_link_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setText(self.replay_data.get('tags', ''))
        self.tags_edit.setPlaceholderText("Separate tags with commas")
        form_layout.addRow("Tags:", self.tags_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(self.replay_data.get('description', ''))
        self.description_edit.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Date Added (read-only)
        date_added = self.replay_data.get('date_added', 'Unknown')
        date_label = QLabel(f"Date Added: {date_added}")
        date_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(date_label)
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def save_changes(self):
        """Save changes to the database."""
        file_name = self.file_name_edit.text().strip()
        
        if not file_name:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "File Name cannot be empty."
            )
            return
        
        try:
            # Update replay in database
            self.database.update_replay(
                self.ufc,
                file_name=file_name,
                timestamp=self.timestamp_edit.text().strip(),
                video_link=self.video_link_edit.text().strip(),
                tags=self.tags_edit.text().strip(),
                extended_desc=self.description_edit.toPlainText().strip()
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to save changes:\n{str(e)}"
            )


# ==================== ui/themes.py (COMPLETE) ====================
"""Theme management for the application."""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages application themes."""
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply dark theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        # Additional styling
        app.setStyleSheet("""
            QLineEdit::placeholder { color: #A0A0A0; }
            QTextEdit::placeholder { color: #A0A0A0; }
        """)
        
        app.setPalette(palette)
    
    @staticmethod
    def apply_light_theme(app: QApplication):
        """Apply light theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 163, 224))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Additional styling
        app.setStyleSheet("""
            QLineEdit { color: black; background-color: white; }
            QLineEdit::placeholder { color: #606060; }
            QTextEdit { color: black; background-color: white; }
            QTextEdit::placeholder { color: #606060; }
        """)
        
        app.setPalette(palette)
    
    @staticmethod
    def apply_theme(app: QApplication, dark_mode: bool):
        """Apply theme based on dark_mode flag."""
        if dark_mode:
            ThemeManager.apply_dark_theme(app)
        else:
            ThemeManager.apply_light_theme(app)


# ==================== CHECKLIST: What You Should Have Now ====================
"""
PROJECT STRUCTURE CHECKLIST:
============================

RKM_ver2/
├── main.py                          ✅ CREATE THIS (above)
├── core/
│   ├── database.py                  ✅ (from previous artifact)
│   ├── preferences.py               ✅ (from previous artifact)
│   └── constants.py                 ✅ (from previous artifact)
├── ui/
│   ├── main_window.py               ✅ (from previous artifact)
│   ├── themes.py                    ✅ (above)
│   ├── panels/
│   │   ├── left_panel.py            ✅ (from previous artifact)
│   │   ├── center_panel.py          ✅ (above)
│   │   └── right_panel.py           ✅ (from previous artifact)
│   ├── dialogs/
│   │   ├── filter_dialogs.py        ✅ (from previous artifact)
│   │   ├── edit_dialog.py           ✅ (above)
│   │   └── character_dialogs.py     ✅ (from previous artifact)
│   └── widgets/
│       ├── replay_table.py          ✅ (from previous artifact)
│       └── search_bar.py            ✅ (above)
└── utils/
    ├── portrait_manager.py          ✅ (from previous artifact)
    ├── quote_manager.py             ✅ (from previous artifact)
    └── helpers.py                   ⚠️ (optional, not created yet)


MISSING/OPTIONAL COMPONENTS:
============================

1. ⚠️ Recycle Bin Dialog - Do you want this?
2. ⚠️ Find & Replace Dialog - Do you want this?
3. ⚠️ CSV Export functionality - Basic version included, enhanced?
4. ⚠️ Backup/Restore dialogs - Basic functionality included
5. ⚠️ About Dialog - Basic version included


ASSETS REQUIRED:
================
Make sure these directories exist with files:

D:\2025\Video Games\Street Fighter 6\RKM\assets\
├── RKM_character_portraits\        ✅ (character images)
├── RKM_rank_portraits\             ✅ (rank badges)
└── RKM_character_quotes\
    └── RKM_character_quotes.json   ✅ (quotes file)


DATABASE:
=========
Will be auto-created at:
D:\2025\Video Games\Street Fighter 6\RKM\database(s)\
"""


# ==================== QUICK START GUIDE ====================
"""
HOW TO RUN YOUR APP:
====================

1. Make sure you have all the files from the artifacts above

2. Open terminal in RKM_ver2 directory

3. Run:
   python main.py

4. If you get import errors:
   - Check that all .py files are in the correct folders
   - Run: pip install PyQt6
   
5. First run will:
   - Prompt you to create or select a database
   - Load preferences
   - Show the main window


NEXT STEPS AFTER RUNNING:
=========================

1. Test basic functionality:
   - Add a replay
   - Search for it
   - Edit it
   - Change character portraits

2. Let me know what's not working or what features you want to add!
"""