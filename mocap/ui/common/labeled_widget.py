from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LabeledWidget(QWidget):
    """Utility widget with a label and a child widget, for cleaner UI sections."""

    def __init__(self, title, widget, parent=None, style="h2"):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setProperty("class", style)
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
