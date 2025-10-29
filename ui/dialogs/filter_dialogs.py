"""Filter dialogs for tag and recorded status filtering."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QGroupBox,
    QRadioButton, QButtonGroup, QWidget
)
from PyQt6.QtCore import Qt
from typing import Optional


class TagFilterDialog(QDialog):
    """Dialog for filtering replays by tags."""
    
    def __init__(self, all_tags: list, current_tags: Optional[list] = None, 
                 use_and: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Filter by Tags")
        self.resize(450, 550)
        
        self.selected_tags = current_tags or []
        self.use_and_logic = use_and
        
        self.init_ui(all_tags)
    
    def init_ui(self, all_tags: list):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        instruction_label = QLabel(
            "Select tags to filter by. You can choose multiple tags."
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        self.tag_checkboxes: dict = {}
        
        if not all_tags:
            no_tags_label = QLabel("No tags found in the database.")
            no_tags_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_tags_label)
        else:
            list_widget = QListWidget()
            list_widget.setMaximumHeight(300)
            
            for tag in all_tags:
                item = QListWidgetItem(list_widget)
                checkbox = QCheckBox(tag)
                checkbox.setChecked(tag in self.selected_tags)
                list_widget.setItemWidget(item, checkbox)
                self.tag_checkboxes[tag] = checkbox
            
            layout.addWidget(list_widget)
            
            select_buttons_layout = QHBoxLayout()
            
            btn_select_all = QPushButton("Select All")
            btn_select_all.clicked.connect(self._select_all)
            select_buttons_layout.addWidget(btn_select_all)
            
            btn_deselect_all = QPushButton("Deselect All")
            btn_deselect_all.clicked.connect(self._deselect_all)
            select_buttons_layout.addWidget(btn_deselect_all)
            
            layout.addLayout(select_buttons_layout)
            
            logic_group = QGroupBox("Filter Logic")
            logic_layout = QVBoxLayout(logic_group)
            
            self.radio_or = QRadioButton("Show replays with ANY selected tag (OR)")
            self.radio_and = QRadioButton("Show replays with ALL selected tags (AND)")
            
            if self.use_and_logic:
                self.radio_and.setChecked(True)
            else:
                self.radio_or.setChecked(True)
            
            logic_layout.addWidget(self.radio_or)
            logic_layout.addWidget(self.radio_and)
            
            layout.addWidget(logic_group)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _select_all(self):
        """Select all tag checkboxes."""
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Deselect all tag checkboxes."""
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_tags(self) -> list:
        """Get list of selected tags."""
        return [tag for tag, checkbox in self.tag_checkboxes.items() 
                if checkbox.isChecked()]
    
    def get_use_and_logic(self) -> bool:
        """Get whether to use AND logic."""
        return self.radio_and.isChecked() if hasattr(self, 'radio_and') else False


class RecordedFilterDialog(QDialog):
    """Dialog for filtering by recorded status."""
    
    def __init__(self, current_filter: Optional[bool] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Filter by Recorded Status")
        self.resize(350, 200)
        
        self.recorded_filter = current_filter
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        instruction_label = QLabel(
            "Choose which replays to display based on recorded status:"
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        self.button_group = QButtonGroup(self)
        
        self.radio_all = QRadioButton("Show All Replays")
        self.radio_recorded = QRadioButton("Show Only Recorded")
        self.radio_not_recorded = QRadioButton("Show Only Not Recorded")
        
        self.button_group.addButton(self.radio_all, 0)
        self.button_group.addButton(self.radio_recorded, 1)
        self.button_group.addButton(self.radio_not_recorded, 2)
        
        # Set current selection
        if self.recorded_filter is None:
            self.radio_all.setChecked(True)
        elif self.recorded_filter is True:
            self.radio_recorded.setChecked(True)
        else:
            self.radio_not_recorded.setChecked(True)
        
        layout.addWidget(self.radio_all)
        layout.addWidget(self.radio_recorded)
        layout.addWidget(self.radio_not_recorded)
        
        layout.addSpacing(20)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_recorded_filter(self) -> Optional[bool]:
        """Get the selected recorded filter."""
        if self.radio_all.isChecked():
            return None
        elif self.radio_recorded.isChecked():
            return True
        else:
            return False