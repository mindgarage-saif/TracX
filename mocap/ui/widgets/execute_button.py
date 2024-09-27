from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from Pose2Sim_with_2d import main
class Execute_button(QWidget):
    def __init__(self, parent: QWidget,info_storage) -> None:
        super().__init__(parent)
        self.settings_store = info_storage
        self.innerLayout = QVBoxLayout(self)
        self.motionEstimationButton = QPushButton("Motion Estimation")
        self.motionEstimationButton.clicked.connect(self.execute)
        self.innerLayout.addWidget(self.motionEstimationButton)

    def execute(self):
        settings = self.settings_store.read()
        main(settings["video_list"],settings["calibration"],settings["config"],settings["rotate"],opensim=settings['openSim'],blender=settings['blender'])