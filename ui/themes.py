"""Theme management with better contrast for readability."""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages application themes with improved contrast."""
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply dark theme with high contrast for readability."""
        palette = QPalette()
        
        # Main window colors - Darker backgrounds
        palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))          # Darker
        palette.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))   # Lighter text
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))            # Input backgrounds - lighter than window
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 55))   # Alternating rows
        
        # Text colors - High contrast
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))         # Very light text
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))   # White for emphasis
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))   # Light button text
        
        # Interactive elements
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))          # Lighter buttons
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 180, 255))         # Brighter blue links
        palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 130, 180))     # Steel blue highlight
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Tooltips
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        
        app.setPalette(palette)
        
        # Enhanced stylesheet for better contrast
        app.setStyleSheet("""
            /* Input fields - clearly visible */
            QLineEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #4682b4;
                background-color: #404040;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
            
            /* Text areas */
            QTextEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border: 1px solid #4682b4;
            }
            
            /* Buttons - high contrast */
            QPushButton {
                background-color: #505050;
                color: #f0f0f0;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px 12px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #606060;
                border: 1px solid #4682b4;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #777777;
            }
            
            /* Dropdown menus */
            QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox:hover {
                border: 1px solid #4682b4;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #f0f0f0;
                selection-background-color: #4682b4;
            }
            
            /* Table - high contrast */
            QTableView {
                background-color: #3a3a3a;
                alternate-background-color: #424242;
                color: #f0f0f0;
                gridline-color: #555555;
                border: 1px solid #555555;
            }
            QTableView::item {
                padding: 4px;
            }
            QTableView::item:selected {
                background-color: #4682b4;
                color: #ffffff;
            }
            QTableView::item:hover {
                background-color: #505050;
            }
            
            /* Headers */
            QHeaderView::section {
                background-color: #505050;
                color: #f0f0f0;
                border: 1px solid #666666;
                padding: 6px;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #606060;
            }
            
            /* Group boxes */
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                color: #f0f0f0;
            }
            QGroupBox::title {
                color: #f0f0f0;
                subcontrol-origin: margin;
                padding: 0 5px;
            }
            
            /* Labels */
            QLabel {
                color: #e6e6e6;
            }
            
            /* Checkboxes */
            QCheckBox {
                color: #e6e6e6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #4682b4;
                border: 1px solid #4682b4;
            }
            
            /* Radio buttons */
            QRadioButton {
                color: #e6e6e6;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #666666;
                border-radius: 7px;
                background-color: #3a3a3a;
            }
            QRadioButton::indicator:checked {
                background-color: #4682b4;
                border: 2px solid #4682b4;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666666;
            }
            QScrollBar:horizontal {
                background: #2a2a2a;
                height: 12px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: #555555;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #666666;
            }
        """)
    
    @staticmethod
    def apply_light_theme(app: QApplication):
        """Apply light theme with proper contrast."""
        palette = QPalette()
        
        # Main window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(20, 20, 20))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 248, 248))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(20, 20, 20))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(20, 20, 20))
        
        # Interactive elements
        palette.setColor(QPalette.ColorRole.Button, QColor(235, 235, 235))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 130, 180))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Tooltips
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(20, 20, 20))
        
        app.setPalette(palette)
        
        # Light theme stylesheet
        app.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #141414;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #4682b4;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
            
            QTextEdit {
                background-color: white;
                color: #141414;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border: 1px solid #4682b4;
            }
            
            QPushButton {
                background-color: #e8e8e8;
                color: #141414;
                border: 1px solid #b0b0b0;
                border-radius: 4px;
                padding: 6px 12px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4682b4;
            }
            QPushButton:pressed {
                background-color: #c8c8c8;
            }
            
            QTableView {
                background-color: white;
                alternate-background-color: #f8f8f8;
                color: #141414;
                gridline-color: #dddddd;
                border: 1px solid #cccccc;
            }
            QTableView::item:selected {
                background-color: #4682b4;
                color: white;
            }
            QTableView::item:hover {
                background-color: #e8f4ff;
            }
            
            QHeaderView::section {
                background-color: #e8e8e8;
                color: #141414;
                border: 1px solid #b0b0b0;
                padding: 6px;
                font-weight: bold;
            }
        """)
    
    @staticmethod
    def apply_theme(app: QApplication, dark_mode: bool):
        """Apply theme based on dark_mode flag."""
        if dark_mode:
            ThemeManager.apply_dark_theme(app)
        else:
            ThemeManager.apply_light_theme(app)