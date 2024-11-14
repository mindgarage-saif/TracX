from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from mocap.ui.styles import PAD_X


class RadioGroup(QWidget):
    """A labeled group of radio buttons with a customizable orientation and selection signal."""

    selectionChanged = pyqtSignal(QRadioButton)

    def __init__(
        self, label, parent=None, orientation=Qt.Orientation.Horizontal, style="h2"
    ):
        super().__init__(parent)

        # Main layout to hold label and radio buttons
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label setup
        title = QLabel(label)
        title.setProperty("class", style)
        layout.addWidget(title)

        # Radio button group setup
        self.group = QButtonGroup(self)
        self.orientation = orientation

        # Layout for radio buttons
        if orientation == Qt.Orientation.Horizontal:
            self.radioLayout = QHBoxLayout()
        else:
            self.radioLayout = QVBoxLayout()
        self.radioLayout.setContentsMargins(0, 0, 0, 0)
        self.radioLayout.setSpacing(PAD_X)
        layout.addLayout(self.radioLayout)

    def addButton(self, text):
        """Add a radio button to the group with the specified text."""
        button = QRadioButton(text)
        button.toggled.connect(lambda: self.selectionChanged.emit(button))
        self.group.addButton(button)
        self.radioLayout.addWidget(button)
        return button

    def checkedId(self):
        """Return the ID of the checked radio button."""
        return self.group.checkedId()

    def checkedButton(self):
        """Return the checked radio button."""
        return self.group.checkedButton()

    def buttons(self):
        """Return the list of radio buttons in the group."""
        return self.group.buttons()

    def addStretch(self):
        """Add a stretch to the layout."""
        self.radioLayout.addStretch()

    def selectDefault(self):
        """Select the first radio button by default if available."""
        if self.group.buttons():
            self.group.buttons()[0].setChecked(True)
            self.selectionChanged.emit(self.group.buttons()[0])
