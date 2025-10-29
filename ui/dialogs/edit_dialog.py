"""Edit replay dialog."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt


class EditReplayDialog(QDialog):
    """Dialog for editing an existing replay entry."""
    
    def __init__(self, replay_data: dict, database, parent=None):
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