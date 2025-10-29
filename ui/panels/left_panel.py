"""Compact left panel with popup buttons."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTextEdit, QLabel, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt


class LeftPanel(QWidget):
    """Compact left panel - Add Replay focused."""
    
    # Signals
    add_replay_requested = pyqtSignal(dict)
    name_picker_clicked = pyqtSignal()
    controls_clicked = pyqtSignal()
    appearance_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(420)
        self.init_ui()
    
    def init_ui(self):
        """Initialize compact UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # === Add Replay Section (Expanded) ===
        add_group = QGroupBox("Add Replay")
        add_layout = QVBoxLayout(add_group)
        add_layout.setSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # File Name with Name Picker
        name_row = QHBoxLayout()
        self.file_name_input = QLineEdit()
        self.file_name_input.setPlaceholderText("Enter File Name")
        self.name_picker_btn = QPushButton("Name Picker")
        self.name_picker_btn.setMaximumWidth(110)
        self.name_picker_btn.clicked.connect(self.name_picker_clicked.emit)
        name_row.addWidget(self.file_name_input)
        name_row.addWidget(self.name_picker_btn)
        form_layout.addRow("File Name:", name_row)
        
        # Timestamp
        self.timestamp_input = QLineEdit()
        self.timestamp_input.setPlaceholderText("e.g., 01:23")
        form_layout.addRow("Timestamp:", self.timestamp_input)
        
        # Description (MORE SPACE)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description (optional)")
        self.description_input.setMinimumHeight(80)  # More room!
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)
        
        # Video Link
        self.video_link_input = QLineEdit()
        self.video_link_input.setPlaceholderText("Video Link (YouTube or Path)")
        form_layout.addRow("Video Link:", self.video_link_input)
        
        add_layout.addLayout(form_layout)
        
        # Add Button (Prominent)
        self.add_button = QPushButton("Add Replay")
        self.add_button.setMinimumHeight(35)
        self.add_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        self.add_button.clicked.connect(self._on_add_clicked)
        add_layout.addWidget(self.add_button)
        
        layout.addWidget(add_group)
        
        # === Popup Buttons Section ===
        popup_group = QGroupBox("Settings")
        popup_layout = QVBoxLayout(popup_group)
        popup_layout.setSpacing(8)
        
        # Controls button
        btn_controls = QPushButton("Controls (Database, Filter, Utility)")
        btn_controls.clicked.connect(self.controls_clicked.emit)
        popup_layout.addWidget(btn_controls)
        
        # Appearance button
        btn_appearance = QPushButton("Appearance (Characters & Theme)")
        btn_appearance.clicked.connect(self.appearance_clicked.emit)
        popup_layout.addWidget(btn_appearance)
        
        layout.addWidget(popup_group)
        
        # === Active Database Label ===
        layout.addSpacing(10)
        db_label_row = QHBoxLayout()
        db_label_row.addWidget(QLabel("Active DB:"))
        self.db_label = QLabel("None")
        self.db_label.setStyleSheet("font-weight: bold;")
        db_label_row.addWidget(self.db_label)
        db_label_row.addStretch()
        layout.addLayout(db_label_row)
        
        layout.addStretch()
    
    def _on_add_clicked(self):
        """Handle add replay button click."""
        data = {
            'file_name': self.file_name_input.text().strip(),
            'timestamp': self.timestamp_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'video_link': self.video_link_input.text().strip()
        }
        self.add_replay_requested.emit(data)
    
    def clear_inputs(self):
        """Clear all input fields."""
        self.file_name_input.clear()
        self.timestamp_input.clear()
        self.description_input.clear()
        self.video_link_input.clear()
    
    def set_active_db(self, db_name: str):
        """Update the active database label."""
        self.db_label.setText(db_name)