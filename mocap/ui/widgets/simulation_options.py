from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class SimulationOptions(QWidget):
    def __init__(self, parent, params):
        super().__init__(parent)
        self.params = params

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
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
        rowLayout = QHBoxLayout(row)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(row)

        # Backend
        label = QLabel("Backend:", self)
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        rowLayout.addWidget(label)

        self.stick = QRadioButton("Stick Figure", self)
        self.stick.setChecked(True)
        self.opensim = QRadioButton("OpenSim", self)
        self.mixamo = QRadioButton("Mixamo", self)
        rowLayout.addWidget(self.stick)
        rowLayout.addWidget(self.opensim)
        rowLayout.addWidget(self.mixamo)
        rowLayout.addStretch()

        self.backend = QButtonGroup(self)
        self.backend.addButton(self.stick)
        self.backend.addButton(self.opensim)
        self.backend.addButton(self.mixamo)

        simulatorOptions = QWidget(self)
        self.simulatorOptions = QHBoxLayout(simulatorOptions)
        self.simulatorOptions.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.addWidget(simulatorOptions)

        label = QLabel("Mode:", self)
        label.setProperty("class", "h3")
        label.setWordWrap(True)
        self.simulatorOptions.addWidget(label)

        self.innerLayout.addStretch()

        buttonBar = QWidget(self)
        buttonBarLayout = QHBoxLayout(buttonBar)
        buttonBarLayout.setContentsMargins(0, 0, 0, 0)

        # Create Button
        createButton = QPushButton("Visualize", self)
        buttonBarLayout.addWidget(createButton)

        downloadButton = QPushButton("Save Visualization", self)
        downloadButton.setEnabled(False)
        buttonBarLayout.addWidget(downloadButton)

        self.innerLayout.addWidget(buttonBar)
