"""Right panel with smaller main character and better rank positioning."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QMouseEvent, QPixmap
from typing import Optional


class RightPanel(QWidget):
    """Right panel with balanced portrait sizes."""
    
    character_clicked = pyqtSignal()
    rank_clicked = pyqtSignal()
    name_clicked = pyqtSignal()
    quote_update_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.main_char_size = 220  # Reduced from 280
        self.rank_size = 140
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize UI with better proportions."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        
        # Character Name
        self.name_label = QLabel("Main Character")
        name_font = QFont("Arial", 13, QFont.Weight.Bold)
        self.name_label.setFont(name_font)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.name_label.mousePressEvent = lambda ev: self.name_clicked.emit()
        self.name_label.setToolTip("Click to edit character name")
        layout.addWidget(self.name_label)
        
        # Main Character Portrait
        self.char_portrait = QLabel()
        self.char_portrait.setFixedSize(self.main_char_size, self.main_char_size)
        self.char_portrait.setStyleSheet("""
            QLabel {
                border: 3px solid #4a4a4a;
                border-radius: 8px;
                background-color: #1a1a1a;
            }
        """)
        self.char_portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.char_portrait.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.char_portrait.mousePressEvent = lambda ev: self.character_clicked.emit()
        self.char_portrait.setToolTip("Click to change main character")
        layout.addWidget(self.char_portrait, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Rank Portrait (below main character)
        self.rank_portrait = QLabel()
        self.rank_portrait.setFixedSize(self.rank_size, self.rank_size)
        self.rank_portrait.setStyleSheet("""
            QLabel {
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                background-color: #1a1a1a;
            }
        """)
        self.rank_portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_portrait.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.rank_portrait.mousePressEvent = lambda ev: self.rank_clicked.emit()
        self.rank_portrait.setToolTip("Click to change rank")
        layout.addWidget(self.rank_portrait, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Quote
        self.quote_label = QLabel("No quotes available")
        quote_font = QFont("Arial", 11)
        quote_font.setItalic(True)
        self.quote_label.setFont(quote_font)
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setFixedWidth(self.main_char_size)
        self.quote_label.setMinimumHeight(50)
        self.quote_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.quote_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
    
    def setup_timer(self):
        self.quote_timer = QTimer(self)
        self.quote_timer.timeout.connect(self.quote_update_requested.emit)
        self.quote_timer.start(60000)
    
    def update_character(self, name: str, pixmap: Optional[QPixmap]):
        self.name_label.setText(f"Main Character: {name}")
        if pixmap:
            self.char_portrait.setPixmap(pixmap)
        else:
            self.char_portrait.clear()
    
    def update_rank(self, pixmap: Optional[QPixmap]):
        if pixmap:
            self.rank_portrait.setPixmap(pixmap)
        else:
            self.rank_portrait.clear()
    
    def update_quote(self, quote: str):
        if quote and quote != "No quotes available":
            self.quote_label.setText(f'"{quote}"')
        else:
            self.quote_label.setText(quote)