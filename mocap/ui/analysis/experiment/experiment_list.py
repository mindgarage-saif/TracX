import os
import subprocess
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mocap.core import Experiment
from mocap.ui.common import IconButton


class ExperimentList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(2)
        self.currentItemChanged.connect(self.onSelectionChanged)
        self.onItemSelected = None

        # Refresh the list
        self.refresh()

    @property
    def experiments(self):
        return Experiment.list()

    def onSelectionChanged(self, current, previous):
        if current and self.onItemSelected is not None:
            self.onItemSelected(current.data(Qt.ItemDataRole.UserRole))

    def getSelection(self) -> Optional[str]:
        currentItem = self.currentItem()
        return currentItem.text() if currentItem else None

    def refresh(self):
        self.clear()
        for exp in self.experiments:
            item = QListWidgetItem(self)
            item_widget = self.createItemWidget(exp)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, exp)
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def createItemWidget(self, exp):
        """Create a custom widget for the experiment item."""
        widget = QWidget(self)
        widget.setProperty("class", "empty")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)

        # Left: Open folder button
        open_button = IconButton("folder.png", 18, parent=widget)
        open_button.clicked.connect(lambda: self.openFolder(exp["path"]))
        layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Right: Experiment name and folder size
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        layout.addLayout(info_layout)
        name_label = QLabel(exp["name"], widget)
        name_label.setProperty("class", "h3")
        size_label = QLabel(self.getFolderSize(exp["path"]), widget)
        size_label.setProperty("class", "body")
        info_layout.addWidget(name_label)
        info_layout.addWidget(size_label)

        layout.addStretch()

        return widget

    def getFolderSize(self, path):
        """Calculate the size of the folder at the given path."""
        try:
            size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(path)
                for filename in filenames
            )
            # Convert to human-readable format
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
        except Exception as e:
            return "Unknown size"

    def openFolder(self, path):
        """Open the folder in the file explorer."""
        if os.name == "nt":  # Windows
            os.startfile(path)
        elif os.name == "posix":  # macOS or Linux
            subprocess.Popen(["xdg-open", path])
