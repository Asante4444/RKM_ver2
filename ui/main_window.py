# ==================== ui/main_window.py (COMPLETE WORKING VERSION) ====================
"""Main application window - Fixed and working."""
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
    QFileDialog, QInputDialog, QApplication, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap
import random
from typing import Optional

from core.database import ReplayDatabase
from core.preferences import Preferences
from core.constants import *
from utils.portrait_manager import PortraitManager
from utils.quote_manager import QuoteManager

from ui.panels.left_panel import LeftPanel
from ui.panels.center_panel import CenterPanel
from ui.panels.right_panel import RightPanel
from ui.widgets.replay_table import ReplayTable
from ui.widgets.search_bar import SearchBar
from ui.themes import ThemeManager
from ui.dialogs.settings_dialogs import ControlsDialog, AppearanceDialog

from ui.dialogs.filter_dialogs import TagFilterDialog, RecordedFilterDialog
from ui.dialogs.edit_dialog import EditReplayDialog
from ui.dialogs.character_dialogs import AltCharacterPickerDialog, NamePickerDialog


class MainWindow(QWidget):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SF6 Replay Knowledge Manager")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)
        
        # Initialize core components with type hints for Pylance
        self.preferences: Preferences = Preferences(PREFERENCES_FILE)
        self.portrait_manager: PortraitManager = PortraitManager(CHAR_PORTRAIT_DIR, RANK_PORTRAIT_DIR)
        self.quote_manager: QuoteManager = QuoteManager(QUOTES_JSON)
        
        # Initialize database
        self.database: Optional[ReplayDatabase] = None
        self._init_database()
        
        # Setup UI
        self.init_ui()
        self.apply_theme()
        
        # Load initial data
        self.load_replays()
        self.update_portraits()
        
        # Setup timers
        self.setup_timers()
    
    def _init_database(self):
        """Initialize database from preferences or prompt user."""
        db_path = self.preferences.get('active_db_path')
        
        if db_path and os.path.exists(db_path):
            self.database = ReplayDatabase(db_path)
        else:
            # Prompt user to select or create database
            self._show_database_dialog()
    
    def show_controls_dialog(self):
        """Show controls popup dialog."""
        dialog = ControlsDialog(self)
        dialog.database_action.connect(self.on_database_action)
        dialog.filter_action.connect(self.on_filter_action)
        dialog.utility_action.connect(self.on_utility_action)
        dialog.exec()

    def show_appearance_dialog(self):
        """Show appearance popup dialog."""
        dialog = AppearanceDialog(self)
        dialog.choose_alts_clicked.connect(self.choose_alt_characters)
        dialog.choose_main_clicked.connect(self.choose_main_character)
        dialog.choose_rank_clicked.connect(self.choose_rank)
        dialog.toggle_theme_clicked.connect(self.toggle_theme)
        dialog.exec()

    def init_ui(self):
        """Initialize the user interface with balanced proportions."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top section with three panels
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)
        
         # Left Panel - UPDATED CONNECTIONS
        self.left_panel = LeftPanel()
        self.left_panel.setMinimumWidth(300)
        self.left_panel.setMaximumWidth(420)
        self.left_panel.add_replay_requested.connect(self.on_add_replay)
        self.left_panel.name_picker_clicked.connect(self.show_name_picker)
        # NEW: Connect popup dialogs
        self.left_panel.controls_clicked.connect(self.show_controls_dialog)
        self.left_panel.appearance_clicked.connect(self.show_appearance_dialog)
        top_layout.addWidget(self.left_panel, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Spacer
        top_layout.addStretch(2)
        
        # Center Panel
        self.center_panel = CenterPanel()
        self.center_panel.setMinimumWidth(220)
        self.center_panel.setMaximumWidth(300)
        self.center_panel.portrait_update_requested.connect(self.update_alt_character)
        top_layout.addWidget(self.center_panel, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Spacer
        top_layout.addStretch(1)
        
        # Right Panel
        self.right_panel = RightPanel()
        self.right_panel.setMinimumWidth(240)
        self.right_panel.setMaximumWidth(300)
        self.right_panel.character_clicked.connect(self.choose_main_character)
        self.right_panel.rank_clicked.connect(self.choose_rank)
        self.right_panel.name_clicked.connect(self.edit_character_name)
        self.right_panel.quote_update_requested.connect(self.update_main_quote)
        top_layout.addWidget(self.right_panel, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Spacer
        top_layout.addStretch(2)
        
        # Add top layout directly (no wrapper, no max height constraint)
        main_layout.addLayout(top_layout)
        
        # Search Bar
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.on_search_changed)
        main_layout.addWidget(self.search_bar)
        
        # Replay Table - gets remaining space
        self.table = ReplayTable()
        self.table.setMinimumHeight(400)
        self.table.recorded_toggled.connect(self.on_recorded_toggled)
        self.table.row_double_clicked.connect(self.on_row_double_clicked)
        main_layout.addWidget(self.table, stretch=1)
        
        # Update active DB label
        if self.database:
            db_name = os.path.basename(self.database.db_path)
            self.left_panel.set_active_db(db_name)
    
    def setup_timers(self):
        """Setup application timers."""
        self.recycle_timer = QTimer(self)
        self.recycle_timer.timeout.connect(self.cleanup_recycle_bin)
        self.recycle_timer.start(RECYCLE_BIN_CHECK_INTERVAL)
    
    # ==================== Database Operations ====================
    
    def on_add_replay(self, data: dict):
        """Handle add replay request."""
        if not self.database:
            QMessageBox.warning(self, "No Database", "Please select or create a database first.")
            return
        
        file_name = data.get('file_name', '').strip()
        if not file_name:
            QMessageBox.warning(self, "Validation Error", "File Name cannot be empty.")
            return
        
        try:
            self.database.add_replay(
                file_name=file_name,
                timestamp=data.get('timestamp', ''),
                video_link=data.get('video_link', ''),
                description=data.get('description', ''),
                tags=""
            )
            
            self.left_panel.clear_inputs()
            self.load_replays()
            QMessageBox.information(self, "Success", "Replay added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add replay:\n{str(e)}")
    
    def load_replays(self):
        """Load replays from database into table."""
        if not self.database:
            return
        
        try:
            replays = self.database.get_all_replays()
            self.table.load_replays(replays)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load replays:\n{str(e)}")
    
    def on_recorded_toggled(self, ufc: str, recorded: bool):
        """Handle recorded checkbox toggle."""
        if not self.database:
            return
        
        try:
            self.database.update_replay(ufc, recorded=1 if recorded else 0)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update recorded status:\n{str(e)}")
    
    def on_row_double_clicked(self, row: int, replay_data: dict):
        """Handle double-click on table row."""
        if not self.database:
            return
        
        dialog = EditReplayDialog(replay_data, self.database, self)
        
        if dialog.exec():
            self.load_replays()
            QMessageBox.information(self, "Success", "Replay updated successfully!")
    
    def cleanup_recycle_bin(self):
        """Auto-cleanup old items from recycle bin."""
        if self.database:
            try:
                self.database.auto_cleanup_recycle_bin(RECYCLE_BIN_AUTO_DELETE_DAYS)
            except Exception as e:
                print(f"Recycle bin cleanup failed: {e}")
    
    # ==================== Database Actions ====================
    
    def on_database_action(self, action: str):
        """Handle database menu actions."""
        if action == 'switch':
            self._show_database_dialog()
        elif action == 'new':
            self._create_new_database()
        elif action == 'backup':
            self._backup_database()
        elif action == 'restore':
            self._restore_database()
    
    def _show_database_dialog(self):
        """Show dialog to select database."""
        try:
            db_files = [f for f in os.listdir(ACTIVE_DB_FOLDER) 
                       if f.lower().endswith('.db')]
        except Exception:
            db_files = []
        
        if not db_files:
            reply = QMessageBox.question(
                self, "No Databases Found",
                "No databases found. Create a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._create_new_database()
            return
        
        db_name, ok = QInputDialog.getItem(
            self, "Select Database", "Choose database:",
            db_files, 0, False
        )
        
        if ok and db_name:
            db_path = os.path.join(ACTIVE_DB_FOLDER, db_name)
            self.database = ReplayDatabase(db_path)
            self.preferences.set('active_db_path', db_path)
            self.left_panel.set_active_db(db_name)
            self.load_replays()
    
    def _create_new_database(self):
        """Create a new database."""
        import uuid
        udc = str(uuid.uuid4())[:8].upper()
        db_name = f"replays_UDC-{udc}.db"
        db_path = os.path.join(ACTIVE_DB_FOLDER, db_name)
        
        self.database = ReplayDatabase(db_path)
        self.preferences.set('active_db_path', db_path)
        self.left_panel.set_active_db(db_name)
        self.load_replays()
        
        QMessageBox.information(self, "Database Created", f"New database created: {db_name}")
    
    def _backup_database(self):
        """Backup current database."""
        if not self.database:
            QMessageBox.warning(self, "No Database", "No active database to backup.")
            return
        
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(self.database.db_path))[0]
        backup_name = f"{base_name}_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DB_FOLDER, backup_name)
        
        try:
            os.makedirs(BACKUP_DB_FOLDER, exist_ok=True)
            shutil.copy2(self.database.db_path, backup_path)
            QMessageBox.information(self, "Backup Created", f"Database backed up to:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Failed to backup database:\n{str(e)}")
    
    def _restore_database(self):
        """Restore database from backup."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Database to Restore",
            BACKUP_DB_FOLDER,
            "Database Files (*.db)"
        )
        
        if not path:
            return
        
        import shutil
        db_name = os.path.basename(path)
        dest_path = os.path.join(ACTIVE_DB_FOLDER, db_name)
        
        try:
            shutil.copy2(path, dest_path)
            self.database = ReplayDatabase(dest_path)
            self.preferences.set('active_db_path', dest_path)
            self.left_panel.set_active_db(db_name)
            self.load_replays()
            QMessageBox.information(self, "Database Restored", f"Database restored: {db_name}")
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"Failed to restore database:\n{str(e)}")
    
    # ==================== Filter Actions ====================
    
    def on_filter_action(self, action: str):
        """Handle filter menu actions."""
        if action == 'tags':
            self._show_tag_filter_dialog()
        elif action == 'recorded':
            self._show_recorded_filter_dialog()
        elif action == 'clear':
            self.search_bar.clear()
            self.table.apply_filters()
    
    def _show_tag_filter_dialog(self):
        """Show tag filter dialog."""
        if not self.database:
            return
        
        all_tags = self.database.get_all_tags()
        
        dialog = TagFilterDialog(
            all_tags=all_tags,
            current_tags=getattr(self, 'current_tag_filter', []),
            use_and=getattr(self, 'use_and_logic', False),
            parent=self
        )
        
        if dialog.exec():
            self.current_tag_filter = dialog.get_selected_tags()
            self.use_and_logic = dialog.get_use_and_logic()
            
            if self.current_tag_filter:
                self.table.apply_filters(
                    search_text=self.search_bar.get_text(),
                    tags=self.current_tag_filter
                )
    
    def _show_recorded_filter_dialog(self):
        """Show recorded filter dialog."""
        current_filter = getattr(self, 'recorded_filter', None)
        
        dialog = RecordedFilterDialog(current_filter, self)
        
        if dialog.exec():
            self.recorded_filter = dialog.get_recorded_filter()
            self.table.apply_filters(
                search_text=self.search_bar.get_text(),
                recorded=self.recorded_filter
            )
    
    def on_search_changed(self, search_text: str):
        """Handle search text changes."""
        self.table.apply_filters(search_text=search_text)
    
    # ==================== Utility Actions ====================
    
    def on_utility_action(self, action: str):
        """Handle utility menu actions."""
        if action == 'export':
            self._export_to_csv()
        elif action == 'refresh':
            self.load_replays()
        elif action == 'about':
            self._show_about_dialog()
    
    def _export_to_csv(self):
        """Export selected rows to CSV."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV",
            "", "CSV Files (*.csv)"
        )
        
        if not path:
            return
        
        QMessageBox.information(self, "Export", "CSV export functionality coming soon!")
    
    def _show_about_dialog(self):
        """Show about dialog."""
        about_text = """
        <h2>SF6 Replay Knowledge Manager</h2>
        <p>Version 2.0</p>
        <p>A comprehensive tool for managing Street Fighter 6 replay metadata.</p>
        <h3>Features:</h3>
        <ul>
            <li>Database management with backup/restore</li>
            <li>Tag-based filtering and organization</li>
            <li>Character portrait and quote rotation</li>
            <li>Dark/Light theme support</li>
        </ul>
        """
        QMessageBox.about(self, "About", about_text)
    
    # ==================== Settings Actions ====================
    
    def choose_alt_characters(self):
        """Show dialog to choose alt characters."""
        current_alts = self.preferences.get_alt_characters()
        
        dialog = AltCharacterPickerDialog(
            self.portrait_manager,
            current_alts,
            self
        )
        
        if dialog.exec():
            selected = dialog.get_selected_characters()
            self.preferences.set_alt_characters(selected)
            self.update_alt_character()
            
            QMessageBox.information(
                self,
                "Alt Characters Updated",
                f"Selected {len(selected)} character(s) for rotation."
            )
    
    def choose_main_character(self):
        """Choose main character portrait."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Character Portrait",
            CHAR_PORTRAIT_DIR,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not path:
            return
        
        self.preferences.set('main_character_path', path)
        
        char_name = self.portrait_manager.clean_filename(os.path.basename(path))
        if char_name:
            self.preferences.set('main_character', char_name)
        
        self.update_portraits()
    
    def choose_rank(self):
        """Choose rank badge."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Rank Badge",
            RANK_PORTRAIT_DIR,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not path:
            return
        
        self.preferences.set('rank_badge_path', path)
        self.update_portraits()
    
    def edit_character_name(self):
        """Edit main character name."""
        current_name = self.preferences.get_main_character() or ""
        
        new_name, ok = QInputDialog.getText(
            self, "Edit Character Name",
            "Enter character name:",
            text=current_name
        )
        
        if ok:
            new_name = new_name.strip()
            if new_name:
                self.preferences.set('character_name_override', new_name)
            else:
                self.preferences.set('character_name_override', None)
            
            self.update_portraits()
    
    def show_name_picker(self):
        """Show name picker dialog."""
        if not self.database:
            QMessageBox.warning(
                self,
                "No Database",
                "Please select a database first."
            )
            return
        
        dialog = NamePickerDialog(self.database, self)
        
        if dialog.exec():
            selected_name = dialog.get_selected_name()
            if selected_name:
                self.left_panel.file_name_input.setText(selected_name)
    
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        current_dark_mode = self.preferences.get('dark_mode', False)
        new_dark_mode = not current_dark_mode
        
        self.preferences.set('dark_mode', new_dark_mode)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme."""
        dark_mode = self.preferences.get('dark_mode', False)
        
        if not isinstance(dark_mode, bool):
            dark_mode = False
        
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            ThemeManager.apply_theme(app, dark_mode)
    
    # ==================== Portrait and Quote Management ====================
    
    def update_portraits(self):
        """Update all portraits."""
        self.update_main_character()
        self.update_rank()
        self.update_alt_character()
        self.update_main_quote()
    
    def update_main_character(self):
        """Update main character display."""
        from core.constants import PORTRAIT_SIZE_MAIN
        
        char_path = self.preferences.get('main_character_path')
        char_name = self.preferences.get_main_character() or "Main Character"
        
        if char_path and os.path.exists(char_path):
            # Use 220x220 to match right panel
            pixmap = self.portrait_manager.load_portrait(
                char_path,
                QSize(220, 220)  # Reduced from 280
            )
            self.right_panel.update_character(char_name, pixmap)
        else:
            self.right_panel.update_character(char_name, None)
    
    def update_rank(self):
        """Update rank portrait."""
        rank_path = self.preferences.get('rank_badge_path')
        
        if rank_path and os.path.exists(rank_path):
            pixmap = self.portrait_manager.load_portrait(
                rank_path,
                QSize(PORTRAIT_SIZE_SMALL, PORTRAIT_SIZE_SMALL)
            )
            self.right_panel.update_rank(pixmap)
        else:
            self.right_panel.update_rank(None)
    
    def update_main_quote(self):
        """Update main character quote."""
        char_name = self.preferences.get_main_character()
        
        if char_name:
            quote = self.quote_manager.get_random_quote(char_name)
            self.right_panel.update_quote(quote)
    
    def update_alt_character(self):
        """Update alt character display."""
        alt_chars = self.preferences.get_alt_characters()
        
        if not alt_chars:
            self.center_panel.update_display("None", None, "No alt characters selected")
            return
        
        char_name = random.choice(alt_chars)
        portraits = self.portrait_manager.get_character_portraits(char_name)
        
        if portraits:
            portrait_path = random.choice(portraits)
            # Use 200x200 to match center panel size
            pixmap = self.portrait_manager.load_portrait(
                portrait_path,
                QSize(200, 200)  # Updated from 160
            )
            quote = self.quote_manager.get_random_quote(char_name)
            self.center_panel.update_display(char_name, pixmap, quote)
        else:
            self.center_panel.update_display(
                char_name, 
                None, 
                "No portrait available"
            )