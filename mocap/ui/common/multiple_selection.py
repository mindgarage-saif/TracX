from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mocap.ui.common import LabeledWidget


class MultipleSelection(LabeledWidget):
    changed = pyqtSignal(list)  # Signal to emit the selected values

    def __init__(self, label, options, parent=None):
        super().__init__(
            label,
            QPushButton("Select Options", parent),
            parent=parent,
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.options = options
        self.selected_options = []

        # Dropdown button
        self.widget.setCheckable(True)

        # Dropdown content
        self.popup = QWidget(self)
        self.popup.setWindowFlags(Qt.WindowType.Popup)
        self.popup_layout = QVBoxLayout(self.popup)
        self.popup_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content for large option lists
        scroll_area = QScrollArea(self.popup)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.popup_layout.addWidget(scroll_area)

        self.checkboxes = {}  # Store checkboxes for each option

        # Add checkboxes
        for key, value in options.items():
            checkbox = QCheckBox(key, self)
            self.checkboxes[value] = checkbox
            scroll_layout.addWidget(checkbox)

        # Close button in popup
        close_button = QPushButton("Done", self.popup)
        close_button.clicked.connect(self.closePopup)
        self.popup_layout.addWidget(close_button)

        # Events
        self.widget.clicked.connect(self.openPopup)

    def openPopup(self):
        # Position the popup below the combo box
        point = self.widget.mapToGlobal(QPoint(0, self.widget.height()))
        self.popup.setGeometry(
            point.x(),
            point.y(),
            self.widget.width(),
            self.popup.sizeHint().height(),
        )
        self.popup.show()

    def closePopup(self):
        self.popup.hide()
        self.widget.setChecked(False)
        self.updateSelection()

    def updateSelection(self):
        self.selected_options = [
            value for value, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]
        self.widget.setText(
            f"{len(self.selected_options)} Selected"
            if self.selected_options
            else "Select Options"
        )
        self.changed.emit(self.selected_options)

    def setOption(self, options):
        for value, checkbox in self.checkboxes.items():
            checkbox.setChecked(value in options)
        self.updateSelection()

    def getSelectedOption(self):
        return self.selected_options
