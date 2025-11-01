"""Custom replay table widget - FIXED TEXT WRAPPING."""
from PyQt6.QtWidgets import (
    QTableView, QHeaderView, QAbstractItemView, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle, QApplication, QWidget
)
from PyQt6.QtGui import (
    QStandardItemModel, QStandardItem, QPalette, QTextDocument, 
    QAbstractTextDocumentLayout, QPainter
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QSize, pyqtSignal, QModelIndex
from typing import Any, Optional


class ElidedTextDelegate(QStyledItemDelegate):
    """Delegate that elides (truncates with ...) long text instead of wrapping."""
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """Paint text with elision for long content."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        style = QApplication.style()
        if style:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter)
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Return fixed height for rows."""
        return QSize(option.rect.width(), 40)  # Fixed row height


class ReplaySortFilterProxy(QSortFilterProxyModel):
    """Custom proxy model for filtering and sorting replays with AND/OR tag logic."""
    
    def __init__(self):
        super().__init__()
        self.search_text = ""
        self.tag_filters: list[str] = []
        self.recorded_filter: Optional[bool] = None
        self.use_and_logic: bool = False
    
    def setSearchText(self, text: str):
        """Set search text filter."""
        self.search_text = text.lower().strip()
        self.invalidateFilter()
    
    def setTagFilter(self, tags: list[str]):
        """Set tag filter."""
        self.tag_filters = [t.lower() for t in tags]
        self.invalidateFilter()
    
    def setRecordedFilter(self, recorded: Optional[bool]):
        """Set recorded status filter."""
        self.recorded_filter = recorded
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Determine if row should be displayed."""
        model = self.sourceModel()
        if not isinstance(model, QStandardItemModel):
            return False
        
        # Get data from columns with type-safe checks
        file_name_item = model.item(source_row, 0)
        desc_item = model.item(source_row, 5)
        tags_item = model.item(source_row, 7)
        recorded_item = model.item(source_row, 3)
        
        if not file_name_item or not desc_item:
            return False
        
        file_name = file_name_item.text().lower()
        description = desc_item.text().lower()
        tags = tags_item.text().lower() if tags_item else ""
        recorded = recorded_item.checkState() == Qt.CheckState.Checked if recorded_item else False
        
        # Search filter
        if self.search_text:
            if not (self.search_text in file_name or 
                   self.search_text in description or
                   self.search_text in tags):
                return False
        
        # Tag filter with AND/OR logic
        if self.tag_filters:
            tag_list = [t.strip().lower() for t in tags.split(',') if t.strip()]
            
            if self.use_and_logic:
                # AND logic: replay must have ALL selected tags
                if not all(ft in tag_list for ft in self.tag_filters):
                    return False
            else:
                # OR logic: replay must have at least ONE selected tag
                if not any(ft in tag_list for ft in self.tag_filters):
                    return False
        
        # Recorded filter
        if self.recorded_filter is not None:
            if recorded != self.recorded_filter:
                return False
        
        return True


class ReplayTable(QTableView):
    """Custom table view for displaying replays."""
    
    row_double_clicked = pyqtSignal(int, dict)
    recorded_toggled = pyqtSignal(str, bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # Store model reference properly
        self._model = QStandardItemModel()
        self.setup_model()
        self.setup_ui()
    
    def setup_model(self):
        """Setup the table model and proxy."""
        self._model.setHorizontalHeaderLabels([
            "File Name", "Timestamp", "UFC", "Recorded", 
            "Video Link", "Description", "Date Added", "Tags"
        ])
        
        self.proxy_model = ReplaySortFilterProxy()
        self.proxy_model.setSourceModel(self._model)
        self.proxy_model.setDynamicSortFilter(True)
        
        self.setModel(self.proxy_model)
    
    def setup_ui(self):
        """Setup UI properties."""
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setWordWrap(False)  # DISABLE word wrap
        
        # Header settings with type-safe checks
        v_header = self.verticalHeader()
        if v_header:
            v_header.setDefaultSectionSize(40)  # Fixed row height
            v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        h_header = self.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            h_header.setStretchLastSection(False)  # Don't stretch last column
        
        # Use elided text delegate for all columns
        self.elided_delegate = ElidedTextDelegate()
        for col in range(8):
            self.setItemDelegateForColumn(col, self.elided_delegate)
        
        # Set column widths
        self.setColumnWidth(0, 150)  # File Name
        self.setColumnWidth(1, 80)   # Timestamp
        self.setColumnWidth(2, 100)  # UFC
        self.setColumnWidth(3, 80)   # Recorded
        self.setColumnWidth(4, 250)  # Video Link
        self.setColumnWidth(5, 200)  # Description
        self.setColumnWidth(6, 140)  # Date Added
        self.setColumnWidth(7, 150)  # Tags
        
        # Set tooltips to show full text on hover
        self.setMouseTracking(True)
        
        # Connect signals
        self.doubleClicked.connect(self._on_double_click)
        self.clicked.connect(self._on_click)
    
    def load_replays(self, replays: list[dict]):
        """Load replay data into the table."""
        self._model.removeRows(0, self._model.rowCount())
        
        for replay in replays:
            items = []
            
            # File Name
            item = QStandardItem(replay.get('file_name', ''))
            item.setEditable(False)
            item.setToolTip(replay.get('file_name', ''))  # Full text on hover
            items.append(item)
            
            # Timestamp
            item = QStandardItem(replay.get('timestamp', ''))
            item.setEditable(False)
            items.append(item)
            
            # UFC
            item = QStandardItem(replay.get('ufc', ''))
            item.setEditable(False)
            items.append(item)
            
            # Recorded (checkable)
            item = QStandardItem()
            item.setCheckable(True)
            item.setCheckState(
                Qt.CheckState.Checked if replay.get('recorded', False) 
                else Qt.CheckState.Unchecked
            )
            items.append(item)
            
            # Video Link
            item = QStandardItem(replay.get('video_link', ''))
            item.setEditable(False)
            item.setToolTip(replay.get('video_link', ''))  # Full text on hover
            items.append(item)
            
            # Description - truncate if too long
            desc = replay.get('description', '')
            item = QStandardItem(desc)
            item.setEditable(False)
            item.setToolTip(desc)  # Full text on hover
            items.append(item)
            
            # Date Added
            item = QStandardItem(replay.get('date_added', ''))
            item.setEditable(False)
            items.append(item)
            
            # Tags
            tags = replay.get('tags', '')
            item = QStandardItem(tags)
            item.setEditable(False)
            item.setToolTip(tags)  # Full text on hover
            items.append(item)
            
            self._model.appendRow(items)
        
        # Don't resize columns to contents - keep fixed widths
    
    def _on_double_click(self, index: QModelIndex):
        """Handle double-click on row to edit."""
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        
        # ✅ TYPE-SAFE: Add null checks for all items
        def safe_text(row: int, col: int) -> str:
            """Safely get text from model item."""
            item = self._model.item(row, col)
            return item.text() if item else ''
        
        replay_data = {
            'file_name': safe_text(row, 0),
            'timestamp': safe_text(row, 1),
            'ufc': safe_text(row, 2),
            'video_link': safe_text(row, 4),
            'description': safe_text(row, 5),
            'date_added': safe_text(row, 6),
            'tags': safe_text(row, 7)
        }
        
        self.row_double_clicked.emit(row, replay_data)
    
    def _on_click(self, index: QModelIndex):
        """Handle click on cell."""
        if index.column() != 3:  # Not the Recorded column
            return
        
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        
        item = self._model.item(row, 3)
        if not item:
            return
            
        new_state = item.checkState() == Qt.CheckState.Checked
        
        ufc_item = self._model.item(row, 2)
        if ufc_item:
            ufc = ufc_item.text()
            self.recorded_toggled.emit(ufc, new_state)
    
    def apply_filters(self, search_text: str = "", tags: Optional[list[str]] = None, 
                     recorded: Optional[bool] = None):
        """Apply filters to the table."""
        self.proxy_model.setSearchText(search_text)
        if tags is not None:
            self.proxy_model.setTagFilter(tags)
        if recorded is not None:
            self.proxy_model.setRecordedFilter(recorded)