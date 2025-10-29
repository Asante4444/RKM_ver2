"""Character selection dialogs."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QDialogButtonBox, QLabel, QLineEdit, QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt
import os


class AltCharacterPickerDialog(QDialog):
    """Dialog for selecting alt characters with checkboxes."""
    
    def __init__(self, portrait_manager, current_alts: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Alt Characters")
        self.resize(450, 600)
        
        self.portrait_manager = portrait_manager
        self.current_alts = current_alts or []
        self.selected_characters = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "Select which characters to rotate in the center panel.\n"
            "Their portraits will cycle every 60 seconds."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter characters...")
        self.search_edit.textChanged.connect(self._filter_characters)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Get all available characters
        available_characters = self._get_available_characters()
        
        if not available_characters:
            no_chars_label = QLabel("No character portraits found.")
            no_chars_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_chars_label)
        else:
            # Character list with checkboxes
            self.list_widget = QListWidget()
            self.list_widget.setMaximumHeight(350)
            
            self.character_items = {}
            
            for char in sorted(available_characters):
                item = QListWidgetItem(self.list_widget)
                checkbox = QCheckBox(char)
                checkbox.setChecked(char in self.current_alts)
                
                self.list_widget.setItemWidget(item, checkbox)
                self.character_items[char] = (item, checkbox)
            
            layout.addWidget(self.list_widget)
            
            # Select buttons
            button_layout = QHBoxLayout()
            
            btn_select_all = QPushButton("Select All")
            btn_select_all.clicked.connect(self._select_all)
            button_layout.addWidget(btn_select_all)
            
            btn_deselect_all = QPushButton("Deselect All")
            btn_deselect_all.clicked.connect(self._deselect_all)
            button_layout.addWidget(btn_deselect_all)
            
            layout.addLayout(button_layout)
        
        # Selected count
        self.count_label = QLabel()
        self._update_count()
        layout.addWidget(self.count_label)
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect checkbox changes to update count
        if hasattr(self, 'character_items'):
            for _, checkbox in self.character_items.values():
                checkbox.stateChanged.connect(self._update_count)
    
    def _get_available_characters(self):
        """Get list of available characters from portrait directory."""
        characters = set()
        
        try:
            portrait_dir = self.portrait_manager.char_dir
            if not os.path.exists(portrait_dir):
                return []
            
            for filename in os.listdir(portrait_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    char_name = self.portrait_manager.clean_filename(filename)
                    if char_name:
                        characters.add(char_name)
        except Exception as e:
            print(f"Error loading characters: {e}")
        
        return sorted(characters)
    
    def _filter_characters(self, search_text: str):
        """Filter character list based on search text."""
        if not hasattr(self, 'character_items'):
            return
        
        search_lower = search_text.lower().strip()
        
        for char, (item, checkbox) in self.character_items.items():
            if item and search_lower in char.lower():
                item.setHidden(False)
            elif item:
                item.setHidden(True)
    
    def _select_all(self):
        """Select all visible characters."""
        if not hasattr(self, 'character_items'):
            return
        
        for char, (item, checkbox) in self.character_items.items():
            if not item.isHidden():
                checkbox.setChecked(True)
        
        self._update_count()
    
    def _deselect_all(self):
        """Deselect all characters."""
        if not hasattr(self, 'character_items'):
            return
        
        for _, (_, checkbox) in self.character_items.values():
            checkbox.setChecked(False)
        
        self._update_count()
    
    def _update_count(self):
        """Update the selected count label."""
        if not hasattr(self, 'character_items'):
            return
        
        count = sum(1 for _, checkbox in self.character_items.values() 
                   if checkbox.isChecked())
        
        self.count_label.setText(f"Selected: {count} character(s)")
        self.count_label.setStyleSheet(
            "font-weight: bold; color: #0066cc;"
        )
    
    def get_selected_characters(self):
        """Get list of selected characters."""
        if not hasattr(self, 'character_items'):
            return []
        
        return [char for char, (_, checkbox) in self.character_items.items() 
                if checkbox.isChecked()]


class NamePickerDialog(QDialog):
    """Dialog for picking/building replay names from existing tags."""
    
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Name Picker")
        self.resize(400, 500)
        
        self.database = database
        self.selected_name = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "Select one or more tags to build a replay name.\n"
            "Hold Ctrl to select multiple tags."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter tags...")
        self.search_edit.textChanged.connect(self._filter_tags)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Get all tags from database
        all_tags = self.database.get_all_tags() if self.database else []
        
        if not all_tags:
            no_tags_label = QLabel("No tags found in database.")
            no_tags_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_tags_label)
        else:
            # Tag list (multi-select)
            self.list_widget = QListWidget()
            self.list_widget.setSelectionMode(
                QListWidget.SelectionMode.ExtendedSelection
            )
            
            for tag in all_tags:
                item = QListWidgetItem(tag)
                self.list_widget.addItem(item)
            
            self.list_widget.itemDoubleClicked.connect(self._on_double_click)
            
            layout.addWidget(self.list_widget)
            
            # Preview
            preview_layout = QVBoxLayout()
            preview_layout.addWidget(QLabel("Preview:"))
            self.preview_label = QLabel("")
            self.preview_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; "
                "background-color: #f0f0f0; font-weight: bold;"
            )
            self.preview_label.setMinimumHeight(30)
            preview_layout.addWidget(self.preview_label)
            layout.addLayout(preview_layout)
            
            # Update preview when selection changes
            self.list_widget.itemSelectionChanged.connect(self._update_preview)
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _filter_tags(self, search_text: str):
        """Filter tag list based on search text."""
        if not hasattr(self, 'list_widget'):
            return
        
        search_lower = search_text.lower().strip()
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item:  # ✅ TYPE-SAFE CHECK ADDED
                if search_lower in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
    
    def _update_preview(self):
        """Update the preview label with selected tags."""
        if not hasattr(self, 'list_widget'):
            return
        
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            tags = [item.text() for item in selected_items]
            self.preview_label.setText("+".join(tags))
        else:
            self.preview_label.setText("")
    
    def _on_double_click(self, item):
        """Handle double-click to instantly select single tag."""
        self.selected_name = item.text()
        self.accept()
    
    def _on_accept(self):
        """Build the selected name from multiple tags."""
        if not hasattr(self, 'list_widget'):
            self.accept()
            return
        
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            tags = [item.text() for item in selected_items]
            self.selected_name = "+".join(tags)
        
        self.accept()
    
    def get_selected_name(self):
        """Get the selected/built name."""
        return self.selected_name