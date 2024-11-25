from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
)

from TracX.ui.common import Tab
from TracX.ui.styles import PAD_Y

from .experiment.create_experiment_dialog import CreateExperimentDialog
from .experiment.experiment_list import ExperimentList


class AnalysisTab(Tab):
    experimentSelected = pyqtSignal(str, dict)

    def __init__(self, parent):
        super().__init__("Motion Analysis", parent, Qt.Orientation.Vertical)
        self.layout.setContentsMargins(0, PAD_Y, 0, 0)
        self.layout.setSpacing(0)

        # Add a title to the page
        title = QLabel("Select Experiment")
        title.setProperty("class", "h3")
        self.addWidget(title)

        # Add instructions
        instructions = QLabel(
            "Select an experiment to start motion estimation or create a new one.",
        )
        instructions.setProperty("class", "body")
        instructions.setWordWrap(True)
        instructions.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum,
        )
        self.addWidget(instructions)
        self.addSpacing(PAD_Y)

        self.experimentList = ExperimentList(self)
        self.experimentList.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
        self.experimentList.onItemSelected = self.emitExperimentSelected
        self.addWidget(self.experimentList)
        self.addSpacing(PAD_Y)

        createButton = QPushButton("New Experiment")
        createButton.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        createButton.clicked.connect(self.createExperiment)
        self.addWidget(createButton)

    def emitExperimentSelected(self, experiment: dict):
        self.experimentSelected.emit(experiment["name"], experiment)

    def createExperiment(self):
        dialog = CreateExperimentDialog(self)
        dialog.setMinimumSize(300, 100)
        dialog.setModal(True)
        dialog.exec()

        self.experimentList.refresh()

    def onSelected(self):
        self.experimentList.refresh()
