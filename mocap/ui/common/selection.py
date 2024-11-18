from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox

from mocap.ui.common import LabeledWidget


class Selection(LabeledWidget):
    changed = pyqtSignal(str)

    def __init__(self, label, options, parent):
        super().__init__(
            label,
            QComboBox(parent),
            parent=parent,
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.options = options
        self.widget.addItems(options.keys())
        self.widget.setMaximumWidth(128)

        def emit():
            selection = self.widget.currentText()
            self.changed.emit(options[selection])

        self.widget.currentIndexChanged.connect(emit)

    def setOption(self, option):
        for key, value in self.options.items():
            if value == option:
                self.widget.setCurrentText(key)
                return

    @property
    def selected_option(self):
        return self.options[self.widget.currentText()]
