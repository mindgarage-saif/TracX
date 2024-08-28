from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel


class Chip(QFrame):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.icon = icon

        # Set the style of the chip
        self.setStyleSheet(
            """
            Chip {
                border-radius: 16px;
                background-color: white;
                padding: 8px;
            }
        """
        )

        # Layout for the content and close button
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)

        # Create a QLabel for the icon
        if self.icon:
            icon_label = QLabel(self)
            icon_pixmap = QPixmap(self.icon)
            icon_label.setPixmap(icon_pixmap.scaled(16, 16))
            layout.addWidget(icon_label)

        self.label = QLabel(self.text)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def setText(self, text):
        self.label.setText(text)
