from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from mocap.ui.tasks import VisualizeTaskConfig

from ..config.constants import PAD_X, PAD_Y
from .buttons import VisualizeMotionButton
from .frame import Frame


class SimulationOptions(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.params = VisualizeTaskConfig()

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(0)

        # Section heading
        heading = QLabel("Simulation", self)
        heading.setProperty("class", "h1")
        self.innerLayout.addWidget(heading)
        self.innerLayout.addSpacing(16)

        # Scaling Settings
        label = QLabel("OpenSim Scaling", self)
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
        rowLayout.addSpacing(PAD_Y)

        # Inverse Kinematics Settings
        label = QLabel("Inverse Kinematics", self)
        label.setProperty("class", "h2")
        label.setWordWrap(True)
        self.innerLayout.addWidget(label)

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
        self.createButton = VisualizeMotionButton(
            self.params, self.onVisualizationsCreated
        )
        buttonBarLayout.addWidget(self.createButton)

        self.downloadButton = QPushButton("Get OpenSim Files", self)
        self.downloadButton.clicked.connect(self.saveVisualizations)
        buttonBarLayout.addWidget(self.downloadButton)

        self.innerLayout.addWidget(buttonBar)

    def onVisualizationsCreated(self, status, result):
        pass

    def saveVisualizations(self):
        print("Saving visualizations")
        pass
