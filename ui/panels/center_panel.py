"""Center panel with better sizing to match right panel."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap
from typing import Optional


class CenterPanel(QWidget):
    """Center panel displaying rotating alt character - improved alignment."""
    
    portrait_update_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # Match the proportions of right panel for consistency
        self.portrait_size = 200  # Increased from 160
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize UI with better sizing and spacing."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)  # Match right panel spacing
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title - match right panel styling
        self.title_label = QLabel("Alt Character: None")
        title_font = QFont("Arial", 13, QFont.Weight.Bold)  # Match right panel
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Portrait - larger and better styled
        self.portrait_label = QLabel()
        self.portrait_label.setFixedSize(self.portrait_size, self.portrait_size)
        self.portrait_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                background-color: #1a1a1a;
            }
        """)
        self.portrait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.portrait_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Quote - match right panel width and styling
        self.quote_label = QLabel("No quotes available")
        quote_font = QFont("Arial", 11)  # Match right panel
        quote_font.setItalic(True)
        self.quote_label.setFont(quote_font)
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setFixedWidth(self.portrait_size)  # Match portrait width
        self.quote_label.setMinimumHeight(60)  # Ensure consistent height
        self.quote_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.quote_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add stretch to push everything up
        layout.addStretch()
    
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
        
        # Format quote consistently with right panel
        if quote and quote != "No quotes available":
            self.quote_label.setText(f'"{quote}"')
        else:
            self.quote_label.setText(quote)