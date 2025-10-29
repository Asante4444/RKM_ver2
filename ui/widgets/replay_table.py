"""Custom replay table widget - TYPE-SAFE VERSION."""
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


class TextWrapDelegate(QStyledItemDelegate):
    """Delegate for text wrapping in table cells."""
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        painter.save()
        doc = QTextDocument()
        doc.setDefaultFont(opt.font)
        doc.setPlainText(opt.text)
        
        text_width = max(1, opt.rect.width())
        doc.setTextWidth(text_width)
        
        opt.text = ""
        style = QApplication.style()
        if style:  # Type-safe check
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter)
        
        painter.translate(opt.rect.x(), opt.rect.y())
        ctx = QAbstractTextDocumentLayout.PaintContext()
        
        if opt.state & QStyle.StateFlag.State_Selected:
            ctx.palette.setColor(
                QPalette.ColorRole.Text,
                opt.palette.color(QPalette.ColorRole.HighlightedText)
            )
        
        layout = doc.documentLayout()
        if layout:  # Type-safe check
            layout.draw(painter, ctx)
        painter.restore()
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        doc = QTextDocument()
        doc.setDefaultFont(opt.font)
        doc.setPlainText(opt.text)
        
        width = opt.rect.width()
        widget = option.widget
        
        if (not width or width <= 0) and widget:
            try:
                # Type-safe widget check
                if isinstance(widget, QTableView):
                    width = widget.columnWidth(index.column())
                else:
                    width = 200
            except:
                width = 200
        
        if not width or width <= 0:
            width = 200
        
        doc.setTextWidth(max(1, width))
        height = int(doc.size().height()) + 6
        
        return QSize(int(width), min(height, 200))


class ReplaySortFilterProxy(QSortFilterProxyModel):
    """Custom proxy model for filtering and sorting replays."""
    
    def __init__(self):
        super().__init__()
        self.search_text = ""
        self.tag_filters: list[str] = []
        self.recorded_filter: Optional[bool] = None
    
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
        desc_item = model.item(source_row, 4)
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
        
        # Tag filter
        if self.tag_filters:
            tag_list = [t.strip() for t in tags.split(',')]
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
        self.setWordWrap(True)
        
        # Header settings with type-safe checks
        v_header = self.verticalHeader()
        if v_header:
            v_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        h_header = self.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            h_header.setStretchLastSection(True)
        
        # Text wrap delegates
        self.wrap_delegate = TextWrapDelegate()
        self.setItemDelegateForColumn(0, self.wrap_delegate)
        self.setItemDelegateForColumn(5, self.wrap_delegate)
        
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
            items.append(item)
            
            # Description
            item = QStandardItem(replay.get('description', ''))
            item.setEditable(False)
            items.append(item)
            
            # Date Added
            item = QStandardItem(replay.get('date_added', ''))
            item.setEditable(False)
            items.append(item)
            
            # Tags
            item = QStandardItem(replay.get('tags', ''))
            item.setEditable(False)
            items.append(item)
            
            self._model.appendRow(items)
        
        self.resizeColumnsToContents()
    
    def _on_double_click(self, index: QModelIndex):
        """Handle double-click on row."""
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        
        # ✅ TYPE-SAFE: Add null checks for all items
        def safe_text(row: int, col: int) -> str:
            """Safely get text from model item."""
            item = self._model.item(row, col)
            return item.text() if item else ''
        
        replay_data = {
            'file_name': safe_text(row, 0),      # ✅ SAFE
            'timestamp': safe_text(row, 1),      # ✅ SAFE
            'ufc': safe_text(row, 2),            # ✅ SAFE
            'video_link': safe_text(row, 4),     # ✅ SAFE
            'description': safe_text(row, 5),    # ✅ SAFE
            'date_added': safe_text(row, 6),     # ✅ SAFE
            'tags': safe_text(row, 7)            # ✅ SAFE
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
