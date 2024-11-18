import os

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton

from mocap.constants import APP_ASSETS


class IconButton(QPushButton):
    def __init__(self, iconFile=None, iconSize=24, parent=None):
        super().__init__(parent)
        self.setObjectName("IconButton")
        self.setStyleSheet("""
            QPushButton#IconButton {
                background-color: #ccc;
                color: #000;
            }
            QPushButton#IconButton:hover {
                background-color: #ddd;
            }
            QPushButton#IconButton:disabled {
                background-color: transparent;
                color: #444;
            }
        """)

        self.setIconFile(iconFile, iconSize)

    def setIconFile(self, iconFile, iconSize):
        if iconFile is None:
            return

        path = os.path.join(APP_ASSETS, "icons", iconFile)
        icon = QIcon(QPixmap(path).scaled(iconSize, iconSize))
        buttonSize = int(iconSize * 1.5)
        self.setFixedSize(buttonSize, buttonSize)
        self.setIconSize(QSize(iconSize, iconSize))
        self.setIcon(icon)
