from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from mocap.core.pipeline import execute_pipeline


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
        execute_pipeline(
            video_files=settings["video_list"],
            calibration_file=settings["calibration"],
            correct_rotation=settings["rotate"],
            visualization_mode="naive",
            # visualization_mode="opensim",
            # visualization_args=dict(
            #     openSim=settings["openSim"],
            #     blender=settings["blender"],
            # ),
        )
