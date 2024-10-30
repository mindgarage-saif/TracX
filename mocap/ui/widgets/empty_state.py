from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class EmptyState(QWidget):
    def __init__(
        self,
        parent: QWidget,
        icon: str,
        label: str,
        action: Optional[str] = None,
        size=300,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        # Load and scale the icon, keeping the aspect ratio
        pixmap = QPixmap(icon)
        pixmap = pixmap.scaledToWidth(size)

        self.icon = QLabel(self)
        self.icon.setPixmap(pixmap)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addWidget(self.icon)

        self.label = QLabel(label, self)
        self.label.setProperty("class", "h2")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedWidth(size)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addWidget(self.label)

        if action:
            self.action = QPushButton(action, self)
            self.action.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            layout.addWidget(self.action, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def setCallback(self, callback):
        self.action.clicked.connect(callback)
