"""Character picker for filename generation."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QDialogButtonBox, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
import os


class FilenameCharacterPickerDialog(QDialog):
    """Dialog for selecting a character to use in filename generation."""
    
    def __init__(self, portrait_manager, current_character: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set File Name Character")
        self.resize(450, 550)
        
        self.portrait_manager = portrait_manager
        self.current_character = current_character
        self.selected_character = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "<b>Choose Character for File Names</b><br><br>"
            "Select a character to use in generated file names.<br>"
            "Format: <code>character_UFC-XXXX_UDC-YYYY_MM-DD-YYYY_HH-MM-SS</code><br><br>"
            "This character will persist until you change it."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        layout.addSpacing(10)
        
        # Current selection
        if self.current_character:
            current_label = QLabel(f"Current: <b>{self.current_character}</b>")
            current_label.setStyleSheet("color: #0066cc; padding: 5px;")
            layout.addWidget(current_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter characters...")
        self.search_edit.textChanged.connect(self._filter_characters)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Get all available characters from portraits
        available_characters = self._get_available_characters()
        
        if not available_characters:
            no_chars_label = QLabel("No character portraits found.")
            no_chars_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_chars_label)
        else:
            # Character list (single selection)
            self.list_widget = QListWidget()
            self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            self.list_widget.setMaximumHeight(300)
            
            for char in sorted(available_characters):
                item = QListWidgetItem(char)
                self.list_widget.addItem(item)
                
                # Highlight current selection
                if char == self.current_character:
                    item.setSelected(True)
            
            self.list_widget.itemDoubleClicked.connect(self._on_double_click)
            self.list_widget.itemSelectionChanged.connect(self._update_preview)
            
            layout.addWidget(self.list_widget)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview filename:"))
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #888;
                padding: 8px;
                background-color: #f0f0f0;
                color: #333;
                font-family: monospace;
                font-size: 9pt;
            }
        """)
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(50)
        preview_layout.addWidget(self.preview_label)
        layout.addLayout(preview_layout)
        
        # Update initial preview
        self._update_preview()
        
        layout.addSpacing(10)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
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
    
    def _update_preview(self):
        """Update the preview label with selected character."""
        selected_items = self.list_widget.selectedItems() if hasattr(self, 'list_widget') else []
        
        if selected_items:
            character = selected_items[0].text()
            # Sanitize character name for filename
            import re
            safe_char = re.sub(r'[\\/:\*\?\"<>\|]', '_', character)
            safe_char = safe_char.lower().replace(" ", "-")
            safe_char = re.sub(r'-+', '-', safe_char).strip('-')
            
            preview = f"{safe_char}_UFC-XXXX_UDC-YYYY_01-15-2025_14-30-45.mp4"
            self.preview_label.setText(preview)
        else:
            self.preview_label.setText("Select a character to see preview")
    
    def _on_double_click(self, item):
        """Handle double-click to instantly select character."""
        self.selected_character = item.text()
        self.accept()
    
    def _on_accept(self):
        """Save the selected character."""
        selected_items = self.list_widget.selectedItems() if hasattr(self, 'list_widget') else []
        
        if selected_items:
            self.selected_character = selected_items[0].text()
        
        self.accept()
    
    def get_selected_character(self):
        """Get the selected character name."""
        return self.selected_character