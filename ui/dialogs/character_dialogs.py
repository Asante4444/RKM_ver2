"""Character selection dialogs and Tag Picker."""
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


class TagPickerDialog(QDialog):
    """Dialog for picking/building tags from existing tags in database."""
    
    def __init__(self, database, current_tags: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag Picker")
        self.resize(450, 550)
        
        self.database = database
        self.current_tags = current_tags
        self.selected_tags = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "Select one or more tags to add to your replay.\n"
            "Hold Ctrl to select multiple tags, or double-click for single selection."
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
            no_tags_label = QLabel("No tags found in database. Enter new tags below.")
            no_tags_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_tags_label)
        else:
            # Tag list (multi-select)
            self.list_widget = QListWidget()
            self.list_widget.setSelectionMode(
                QListWidget.SelectionMode.ExtendedSelection
            )
            self.list_widget.setMaximumHeight(300)
            
            for tag in all_tags:
                item = QListWidgetItem(tag)
                self.list_widget.addItem(item)
            
            self.list_widget.itemDoubleClicked.connect(self._on_double_click)
            self.list_widget.itemSelectionChanged.connect(self._update_preview)
            
            layout.addWidget(self.list_widget)
            
            # Select buttons
            button_layout = QHBoxLayout()
            
            btn_select_all = QPushButton("Select All")
            btn_select_all.clicked.connect(self._select_all)
            button_layout.addWidget(btn_select_all)
            
            btn_clear_selection = QPushButton("Clear Selection")
            btn_clear_selection.clicked.connect(self._clear_selection)
            button_layout.addWidget(btn_clear_selection)
            
            layout.addLayout(button_layout)
        
        # New tag input
        new_tag_layout = QVBoxLayout()
        new_tag_layout.addWidget(QLabel("Or add new tag(s):"))
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("Enter new tag(s), separate with commas")
        self.new_tag_input.textChanged.connect(self._update_preview)
        new_tag_layout.addWidget(self.new_tag_input)
        layout.addLayout(new_tag_layout)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet(
            "border: 1px solid gray; padding: 8px; "
            "background-color: #f0f0f0; font-weight: bold; min-height: 30px;"
        )
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        layout.addLayout(preview_layout)
        
        # Update preview with current tags
        if self.current_tags:
            self.preview_label.setText(self.current_tags)
        
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
            if item:
                if search_lower in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
    
    def _select_all(self):
        """Select all visible tags."""
        if not hasattr(self, 'list_widget'):
            return
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and not item.isHidden():
                item.setSelected(True)
        
        self._update_preview()
    
    def _clear_selection(self):
        """Clear all selected tags."""
        if not hasattr(self, 'list_widget'):
            return
        
        self.list_widget.clearSelection()
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview label with selected tags."""
        tags = []
        
        # Get selected tags from list
        if hasattr(self, 'list_widget'):
            selected_items = self.list_widget.selectedItems()
            tags.extend([item.text() for item in selected_items])
        
        # Get new tags from input
        new_tags = self.new_tag_input.text().strip()
        if new_tags:
            tags.extend([t.strip() for t in new_tags.split(',') if t.strip()])
        
        if tags:
            self.preview_label.setText(", ".join(tags))
        else:
            self.preview_label.setText("")
    
    def _on_double_click(self, item):
        """Handle double-click to instantly select single tag."""
        self.selected_tags = [item.text()]
        self.accept()
    
    def _on_accept(self):
        """Build the selected tags from multiple sources."""
        tags = []
        
        # Get selected tags from list
        if hasattr(self, 'list_widget'):
            selected_items = self.list_widget.selectedItems()
            tags.extend([item.text() for item in selected_items])
        
        # Get new tags from input
        new_tags = self.new_tag_input.text().strip()
        if new_tags:
            tags.extend([t.strip() for t in new_tags.split(',') if t.strip()])
        
        self.selected_tags = tags
        self.accept()
    
    def get_selected_tags(self):
        """Get the selected/built tags as comma-separated string."""
        return ", ".join(self.selected_tags) if self.selected_tags else ""