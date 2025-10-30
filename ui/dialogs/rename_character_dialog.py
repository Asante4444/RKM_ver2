"""Dialog for setting the character name used in file renaming."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QDialogButtonBox, QPushButton, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from typing import Optional
import re


class RenameCharacterDialog(QDialog):
    """Dialog for setting the character name to use in file renaming operations."""
    
    def __init__(self, current_character: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Rename Character")
        self.resize(500, 300)
        
        self.current_character = current_character
        self.selected_character = current_character
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction_label = QLabel(
            "<b>Set Character for File Renaming</b><br><br>"
            "This character name will be used when renaming files.<br>"
            "Files will be renamed in the format:<br>"
            "<code>character_UFC-XXXX_UDC-YYYY_MM-DD-YYYY_HH-MM-SS</code>"
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        layout.addSpacing(15)
        
        # Input group
        input_group = QGroupBox("Character Name")
        input_layout = QVBoxLayout(input_group)
        
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Character:"))
        
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("e.g., Chun-Li, Ken, Ryu")
        if self.current_character:
            self.character_input.setText(self.current_character)
        self.character_input.textChanged.connect(self._update_preview)
        input_row.addWidget(self.character_input)
        
        input_layout.addLayout(input_row)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview filename:"))
        
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #888;
                padding: 8px;
                background-color: #f5f5f5;
                color: #333;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(50)
        preview_layout.addWidget(self.preview_label)
        
        input_layout.addLayout(preview_layout)
        layout.addWidget(input_group)
        
        # Update initial preview
        self._update_preview()
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_character)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)
        
        layout.addLayout(button_layout)
    
    def _update_preview(self):
        """Update the preview label with sanitized filename."""
        character = self.character_input.text().strip()
        
        if character:
            # Sanitize character name for filename
            safe_char = self._sanitize_character_name(character)
            preview = f"{safe_char}_UFC-XXXX_UDC-YYYY_01-15-2025_14-30-45.mp4"
        else:
            preview = "No character set"
        
        self.preview_label.setText(preview)
    
    def _sanitize_character_name(self, name: str) -> str:
        """Sanitize character name for use in filenames."""
        # Remove invalid filename characters
        safe_name = re.sub(r'[\\/:\*\?\"<>\|]', '_', name)
        # Convert to lowercase and replace spaces with hyphens
        safe_name = safe_name.lower().replace(" ", "-")
        # Remove multiple consecutive hyphens
        safe_name = re.sub(r'-+', '-', safe_name)
        # Strip leading/trailing hyphens
        safe_name = safe_name.strip('-')
        return safe_name
    
    def _clear_character(self):
        """Clear the character input."""
        self.character_input.clear()
    
    def _accept(self):
        """Accept the dialog and save the character."""
        character = self.character_input.text().strip()
        
        if character:
            # Validate that sanitized name is not empty
            safe_name = self._sanitize_character_name(character)
            if not safe_name:
                QMessageBox.warning(
                    self,
                    "Invalid Character",
                    "The character name results in an invalid filename.\n"
                    "Please use a different name."
                )
                return
            
            self.selected_character = character
        else:
            self.selected_character = None
        
        self.accept()
    
    def get_character(self) -> Optional[str]:
        """Get the selected character name."""
        return self.selected_character