from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ..config.constants import PAD_X, PAD_Y
from .frame import Frame


class SimulationOptions(Frame):
    def __init__(self, parent, params):
        super().__init__(parent)
        self.params = params

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(0)

        # Section heading
        heading = QLabel("Visualization", self)
        heading.setProperty("class", "h1")
        self.innerLayout.addWidget(heading)
        self.innerLayout.addSpacing(16)

        # Backend
        label = QLabel("Simulation Options", self)
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

        row = QWidget(self)
        row.setProperty("class", "empty")
        rowLayout = QVBoxLayout(row)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(row)

        self.stick = QRadioButton("Stick Figure", self)
        self.stick.setChecked(True)
        self.opensim = QRadioButton("OpenSim", self)
        rowLayout.addWidget(self.stick)
        rowLayout.addWidget(self.opensim)
        rowLayout.addStretch()

        self.backend = QButtonGroup(self)
        self.backend.addButton(self.stick)
        self.backend.addButton(self.opensim)

        simulatorOptions = QWidget(self)
        simulatorOptions.setProperty("class", "empty")
        self.simulatorOptions = QHBoxLayout(simulatorOptions)
        self.simulatorOptions.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(simulatorOptions)

        self.innerLayout.addStretch()

        buttonBar = QWidget(self)
        buttonBar.setProperty("class", "empty")
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        createButton = QPushButton("Visualize", self)
        buttonBarLayout.addWidget(createButton)

        downloadButton = QPushButton("Save Visualization", self)
        downloadButton.setEnabled(False)
        buttonBarLayout.addWidget(downloadButton)

        self.innerLayout.addWidget(buttonBar)
