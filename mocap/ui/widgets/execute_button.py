from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from Pose2Sim_with_2d import run_pipeline


class MotionEstimationButton(QWidget):
    def __init__(self, parent: QWidget, params) -> None:
        super().__init__(parent)
        self.params = params
        self.innerLayout = QVBoxLayout(self)
        self.motionEstimationButton = QPushButton("Motion Estimation")
        self.motionEstimationButton.clicked.connect(self.execute)
        self.innerLayout.addWidget(self.motionEstimationButton)

    def execute(self):
        settings = self.params.read()
        run_pipeline(
            video_files=settings["video_list"],
            calibration_file=settings["calibration"],
            config=settings["config"],
            rotate=settings["rotate"],
            opensim=settings["openSim"],
            blender=settings["blender"],
        )
