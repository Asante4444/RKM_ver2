"""Utility dialogs for Find/Replace and Recycle Bin management."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDialogButtonBox, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from typing import Optional


class FindReplaceDialog(QDialog):
    """Dialog for finding and replacing text in database fields."""
    
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.resize(600, 300)
        
        self.database = database
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "<b>Find and Replace Text</b><br>"
            "Search for text in a specific column and replace it with new text."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        layout.addSpacing(10)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Column selector
        self.column_combo = QComboBox()
        self.column_combo.addItems([
            "File Name",
            "Timestamp", 
            "Video Link",
            "Description",
            "Tags"
        ])
        form_layout.addRow("Search in:", self.column_combo)
        
        # Find text
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Text to find...")
        form_layout.addRow("Find:", self.find_input)
        
        # Replace text
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        form_layout.addRow("Replace with:", self.replace_input)
        
        layout.addLayout(form_layout)
        
        # Case sensitive option
        self.case_sensitive_check = QLineEdit()
        
        # Preview button
        preview_layout = QHBoxLayout()
        self.preview_btn = QPushButton("Preview Changes")
        self.preview_btn.clicked.connect(self._preview_changes)
        preview_layout.addWidget(self.preview_btn)
        
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._apply_replace)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _preview_changes(self):
        """Preview how many entries would be affected."""
        find_text = self.find_input.text().strip()
        
        if not find_text:
            QMessageBox.warning(self, "No Text", "Please enter text to find.")
            return
        
        column_name = self._get_column_name()
        count = self._count_matches(column_name, find_text)
        
        self.preview_label.setText(f"Found {count} match(es)")
    
    def _apply_replace(self):
        """Apply find and replace operation."""
        find_text = self.find_input.text().strip()
        replace_text = self.replace_input.text().strip()
        
        if not find_text:
            QMessageBox.warning(self, "No Text", "Please enter text to find.")
            return
        
        column_name = self._get_column_name()
        count = self._count_matches(column_name, find_text)
        
        if count == 0:
            QMessageBox.information(self, "No Matches", "No matches found.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Replace",
            f"Replace {count} occurrence(s) of:\n'{find_text}'\n\nwith:\n'{replace_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._perform_replace(column_name, find_text, replace_text)
            QMessageBox.information(
                self,
                "Success",
                f"Replaced text in {count} entry/entries."
            )
            self.accept()
    
    def _get_column_name(self) -> str:
        """Get database column name from combo box selection."""
        mapping = {
            "File Name": "file_name",
            "Timestamp": "timestamp",
            "Video Link": "video_link",
            "Description": "extended_desc",
            "Tags": "tags"
        }
        return mapping[self.column_combo.currentText()]
    
    def _count_matches(self, column_name: str, find_text: str) -> int:
        """Count how many entries contain the find text."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    f"SELECT COUNT(*) FROM replays WHERE {column_name} LIKE ?",
                    (f"%{find_text}%",)
                )
                return c.fetchone()[0]
        except Exception as e:
            print(f"Error counting matches: {e}")
            return 0
    
    def _perform_replace(self, column_name: str, find_text: str, replace_text: str):
        """Perform the replace operation."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    f"UPDATE replays SET {column_name} = REPLACE({column_name}, ?, ?) WHERE {column_name} LIKE ?",
                    (find_text, replace_text, f"%{find_text}%")
                )
                conn.commit()
        except Exception as e:
            print(f"Error performing replace: {e}")
            raise


class RecycleBinDialog(QDialog):
    """Dialog for viewing and managing recycle bin entries."""
    
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recycle Bin")
        self.resize(900, 600)
        
        self.database = database
        self.init_ui()
        self.load_recycled_items()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "<b>Recycle Bin</b><br>"
            "Deleted replays are kept here for 30 days before permanent deletion."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "File Name", "UFC", "Deleted Date", "Video Link", "Tags", "Description"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # Set column widths
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 200)
        
        layout.addWidget(self.table)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.clicked.connect(self._restore_selected)
        button_layout.addWidget(self.restore_btn)
        
        self.delete_btn = QPushButton("Delete Permanently")
        self.delete_btn.clicked.connect(self._delete_permanently)
        button_layout.addWidget(self.delete_btn)
        
        self.empty_btn = QPushButton("Empty Recycle Bin")
        self.empty_btn.clicked.connect(self._empty_recycle_bin)
        self.empty_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        button_layout.addWidget(self.empty_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_recycled_items(self):
        """Load recycled items from database."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT file_name, ufc, deleted_date, video_link, tags, extended_desc
                    FROM recycle_bin
                    ORDER BY deleted_date DESC
                """)
                rows = c.fetchall()
            
            self.table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value else "")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(i, j, item)
            
            # Update info label
            count = len(rows)
            info_text = f"<b>Recycle Bin</b><br>{count} deleted replay(s)"
            self.findChild(QLabel).setText(info_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load recycle bin:\n{str(e)}")
    
    def _restore_selected(self):
        """Restore selected items from recycle bin."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select items to restore.")
            return
        
        ufc_list = []
        for row in selected_rows:
            ufc_item = self.table.item(row, 1)
            if ufc_item:
                ufc_list.append(ufc_item.text())
        
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Restore {len(ufc_list)} item(s) to the main table?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._restore_items(ufc_list)
            self.load_recycled_items()
            QMessageBox.information(self, "Success", f"Restored {len(ufc_list)} item(s).")
    
    def _delete_permanently(self):
        """Permanently delete selected items."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select items to delete.")
            return
        
        ufc_list = []
        for row in selected_rows:
            ufc_item = self.table.item(row, 1)
            if ufc_item:
                ufc_list.append(ufc_item.text())
        
        reply = QMessageBox.warning(
            self,
            "Confirm Permanent Delete",
            f"⚠️ PERMANENTLY delete {len(ufc_list)} item(s)?\n\nThis CANNOT be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._delete_items(ufc_list)
            self.load_recycled_items()
            QMessageBox.information(self, "Success", f"Permanently deleted {len(ufc_list)} item(s).")
    
    def _empty_recycle_bin(self):
        """Empty the entire recycle bin."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM recycle_bin")
                count = c.fetchone()[0]
            
            if count == 0:
                QMessageBox.information(self, "Empty", "Recycle bin is already empty.")
                return
            
            reply = QMessageBox.warning(
                self,
                "Confirm Empty Recycle Bin",
                f"⚠️ PERMANENTLY delete ALL {count} item(s) from recycle bin?\n\nThis CANNOT be undone!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                with sqlite3.connect(self.database.db_path) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM recycle_bin")
                    conn.commit()
                
                self.load_recycled_items()
                QMessageBox.information(self, "Success", "Recycle bin emptied.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to empty recycle bin:\n{str(e)}")
    
    def _restore_items(self, ufc_list: list):
        """Restore items from recycle bin to main table."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                
                for ufc in ufc_list:
                    # Get data from recycle bin
                    c.execute("""
                        SELECT video_link, file_name, timestamp, ufc, extended_desc,
                               recorded, renamed_filename, date_added, tags
                        FROM recycle_bin WHERE ufc = ?
                    """, (ufc,))
                    
                    data = c.fetchone()
                    if not data:
                        continue
                    
                    # Insert back into replays
                    c.execute("""
                        INSERT INTO replays (video_link, file_name, timestamp, ufc,
                                            extended_desc, recorded, renamed_filename,
                                            date_added, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, data)
                    
                    # Delete from recycle bin
                    c.execute("DELETE FROM recycle_bin WHERE ufc = ?", (ufc,))
                
                conn.commit()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore items:\n{str(e)}")
    
    def _delete_items(self, ufc_list: list):
        """Permanently delete items from recycle bin."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                c = conn.cursor()
                
                for ufc in ufc_list:
                    c.execute("DELETE FROM recycle_bin WHERE ufc = ?", (ufc,))
                
                conn.commit()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete items:\n{str(e)}")