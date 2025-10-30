"""Popup dialogs for Controls and Appearance settings."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDialogButtonBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class ControlsDialog(QDialog):
    """Popup dialog for Database, Filter, and Utility controls."""
    
    database_action = pyqtSignal(str)
    filter_action = pyqtSignal(str)
    utility_action = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controls")
        self.resize(400, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize controls dialog."""
        layout = QVBoxLayout(self)
        
        # Database Section
        db_group = QGroupBox("Database")
        db_layout = QVBoxLayout(db_group)
        
        btn_choose_db = QPushButton("Choose Active Database")
        btn_choose_db.clicked.connect(lambda: self.database_action.emit('switch'))
        db_layout.addWidget(btn_choose_db)
        
        btn_new_db = QPushButton("Create New Database")
        btn_new_db.clicked.connect(lambda: self.database_action.emit('new'))
        db_layout.addWidget(btn_new_db)
        
        btn_backup = QPushButton("Backup Database")
        btn_backup.clicked.connect(lambda: self.database_action.emit('backup'))
        db_layout.addWidget(btn_backup)
        
        btn_restore = QPushButton("Restore Database")
        btn_restore.clicked.connect(lambda: self.database_action.emit('restore'))
        db_layout.addWidget(btn_restore)
        
        layout.addWidget(db_group)
        
        # Filter Section
        filter_group = QGroupBox("Filter")
        filter_layout = QVBoxLayout(filter_group)
        
        btn_filter_tags = QPushButton("Filter by Tags")
        btn_filter_tags.clicked.connect(lambda: self.filter_action.emit('tags'))
        filter_layout.addWidget(btn_filter_tags)
        
        btn_filter_recorded = QPushButton("Filter by Recorded")
        btn_filter_recorded.clicked.connect(lambda: self.filter_action.emit('recorded'))
        filter_layout.addWidget(btn_filter_recorded)
        
        btn_clear_filters = QPushButton("Clear Filters")
        btn_clear_filters.clicked.connect(lambda: self.filter_action.emit('clear'))
        filter_layout.addWidget(btn_clear_filters)
        
        layout.addWidget(filter_group)
        
        # Utility Section
        utility_group = QGroupBox("Utility")
        utility_layout = QVBoxLayout(utility_group)
        
        # NEW: Rename character button
        btn_set_rename_char = QPushButton("Set Rename Character")
        btn_set_rename_char.clicked.connect(lambda: self.utility_action.emit('set_rename_character'))
        utility_layout.addWidget(btn_set_rename_char)
        
        # NEW: Rename files button
        btn_rename_files = QPushButton("Rename Selected Files")
        btn_rename_files.clicked.connect(lambda: self.utility_action.emit('rename_files'))
        utility_layout.addWidget(btn_rename_files)
        
        btn_export = QPushButton("Export to CSV")
        btn_export.clicked.connect(lambda: self.utility_action.emit('export'))
        utility_layout.addWidget(btn_export)
        
        btn_refresh = QPushButton("Refresh Table")
        btn_refresh.clicked.connect(lambda: self.utility_action.emit('refresh'))
        utility_layout.addWidget(btn_refresh)
        
        btn_about = QPushButton("About")
        btn_about.clicked.connect(lambda: self.utility_action.emit('about'))
        utility_layout.addWidget(btn_about)
        
        layout.addWidget(utility_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class AppearanceDialog(QDialog):
    """Popup dialog for Appearance settings."""
    
    choose_alts_clicked = pyqtSignal()
    choose_main_clicked = pyqtSignal()
    choose_rank_clicked = pyqtSignal()
    toggle_theme_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Appearance Settings")
        self.resize(350, 200)
        self.init_ui()
    
    def init_ui(self):
        """Initialize appearance dialog."""
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Character & Theme Settings")
        group_layout = QVBoxLayout(group)
        
        btn_alts = QPushButton("Choose Alt Characters")
        btn_alts.clicked.connect(self.choose_alts_clicked.emit)
        group_layout.addWidget(btn_alts)
        
        btn_main = QPushButton("Choose Main Character")
        btn_main.clicked.connect(self.choose_main_clicked.emit)
        group_layout.addWidget(btn_main)
        
        btn_rank = QPushButton("Choose Rank Badge")
        btn_rank.clicked.connect(self.choose_rank_clicked.emit)
        group_layout.addWidget(btn_rank)
        
        btn_theme = QPushButton("Toggle Dark/Light Theme")
        btn_theme.clicked.connect(self.toggle_theme_clicked.emit)
        group_layout.addWidget(btn_theme)
        
        layout.addWidget(group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)