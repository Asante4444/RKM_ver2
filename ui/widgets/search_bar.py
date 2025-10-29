"""Search bar widget for filtering replays."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal


class SearchBar(QWidget):
    """Search bar for filtering replays."""
    
    search_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Search:")
        layout.addWidget(label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, tags, or description...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)
    
    def clear(self):
        """Clear the search input."""
        self.search_input.clear()
    
    def get_text(self) -> str:
        """Get current search text."""
        return self.search_input.text()