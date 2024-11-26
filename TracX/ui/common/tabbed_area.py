import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from TracX.ui.styles import PAD_X, PAD_Y


def slugify(text):
    return re.sub(r"\s+", "-", text.strip().lower())


class Tab(QWidget):
    def __init__(self, title, parent, orientation=Qt.Orientation.Horizontal):
        assert isinstance(parent, TabbedArea), "Parent must be a TabbedArea"
        super().__init__(parent)
        self.setObjectName("Tab")
        self.name = slugify(title)
        self.title = title

        # Create a layout
        if orientation == Qt.Orientation.Horizontal:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.setLayout(self.layout)

    def addWidget(self, widget):
        self.layout.addWidget(widget)

    def addSpacing(self, size):
        self.layout.addSpacing(size)

    def onSelected(self):
        """
        Called when the tab is selected.
        Should be implemented by subclasses.
        """


class TabbedArea(QFrame):
    """
    A tabbed area that can be used to switch between different views.
    """

    selected = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("TabbedArea")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)

        self.tabs = QTabWidget(self)
        self.layout.addWidget(self.tabs)

        self.names = []
        self.tabs.currentChanged.connect(self.onTabChanged)

    def addTab(self, tab):
        assert tab.name not in self.names, "Tab names must be unique"

        self.tabs.addTab(tab, tab.title)
        self.names.append(tab.name)

    def onTabChanged(self, index):
        tab: Tab = self.tabs.widget(index)
        tab.onSelected()
        self.selected.emit(index)

    def selectTab(self, index):
        self.tabs.setCurrentIndex(index)

    def selectTabByName(self, name):
        for i, tab in enumerate(self.tabs):
            if tab.name == name:
                self.tabs.setCurrentIndex(i)
                break
