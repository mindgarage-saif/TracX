from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from TracX.ui.analysis import EstimateMotionButton, KinematicsButton
from TracX.ui.common import IconButton
from TracX.ui.styles import PAD_X, PAD_Y


class SettingsPanel(QFrame):
    def __init__(self, title, parent, width=320):
        super().__init__(parent)
        self.setObjectName("SettingsPanel")
        self.title = title
        self.experiment = None
        self.setFixedWidth(width)
        self.initUI()

    def initScrollAreaContent(self, scroll_layout):
        pass

    def initButtonBar(self, main_layout):
        button_bar = QWidget(self)
        button_bar.setProperty("class", "empty")
        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Save Button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.applyConfigChanges)
        layout.addWidget(self.saveButton)

        # Estimate Motion Button
        self.analyzeButton = EstimateMotionButton(self.onAnalyzed)
        layout.addWidget(self.analyzeButton)

        # Download Button
        self.exportButton = IconButton("export.png", 24, self)
        layout.addWidget(self.exportButton)

        self.visualizeButton = KinematicsButton(self.onVisualized)
        layout.addWidget(self.visualizeButton)

        main_layout.addWidget(button_bar)

    def initUI(self):
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        main_layout.setSpacing(0)

        # Section heading
        self.name_label = QLabel("", self)
        self.name_label.setProperty("class", "h1")
        main_layout.addWidget(self.name_label)

        self.title_label = QLabel(self.title, self)
        self.title_label.setProperty("class", "h2")
        self.title_label.setStyleSheet("font-weight: normal;")
        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(PAD_Y)

        # Create a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create a container widget for the scroll area
        scroll_content = QWidget(scroll_area)
        scroll_content.setProperty("class", "empty")
        scroll_content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)
        scroll_layout.setContentsMargins(0, 0, PAD_X, 0)
        scroll_layout.setSpacing(PAD_Y // 4)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Add content to the scroll area
        self.initScrollAreaContent(scroll_layout)

        # Final stretch
        scroll_layout.addStretch()
        main_layout.addSpacing(PAD_Y)

        # Button Bar
        self.initButtonBar(main_layout)

    def setExperiment(self, experiment):
        """Set the experiment object.

        Args:
            experiment (Experiment): The experiment object.

        """
        self.experiment = experiment
        self.refreshUI()

    def refreshUI(self):
        if self.experiment is None:
            return

        self.name_label.setText(self.experiment.name)
        cfg = self.experiment.cfg

        self.pose_model.setOption(cfg["pose"]["pose_model"])
        self.perfomance_mode.setOption(cfg["pose"]["mode"])
        self.det_frequency.widget.setText(str(cfg["pose"]["det_frequency"]))

        # Update buttons
        self.analyzeButton.task.experiment = self.experiment.name
        self.visualizeButton.task.experiment = self.experiment.name

    def updateConfig(self, cfg):
        """Read the configuration from the UI components.

        Args:
            cfg (dict): The configuration dictionary.

        """
        # Pose settings
        cfg["pose"]["pose_model"] = self.pose_model.selected_option
        cfg["pose"]["mode"] = self.perfomance_mode.selected_option
        cfg["pose"]["det_frequency"] = int(self.det_frequency.widget.text())

        return cfg

    def applyConfigChanges(self):
        cfg = self.updateConfig(self.experiment.cfg)
        self.experiment.update_config(cfg)

    def onAnalyzed(self, status, result):
        pass

    def onVisualized(self, status, result):
        pass
