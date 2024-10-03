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
from Pose2Sim_with_2d import main,do_it
import threading


def run_in_thread(target_function, *args, **kwargs):
    # Create a new thread and pass the target function along with its arguments
    thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
    thread.start()

class Execute_button(QWidget):
    def __init__(self, parent: QWidget,  info_storage) -> None:
        super().__init__(parent)
        self.settings_store = info_storage
        self.innerLayout = QVBoxLayout(self)
        self.motionEstimationButton = QPushButton("Motion Estimation")
        self.motionEstimationButton.clicked.connect(self.execute)
        self.innerLayout.addWidget(self.motionEstimationButton)

    def execute(self):
        # Read settings from info_storage
        settings = self.settings_store.read()
        
        # Extract the necessary arguments
        video_list = settings["video_list"]
        calibration = settings["calibration"]
        config = settings["config"]
        rotate = settings["rotate"]
        opensim = settings["openSim"]
        blender = settings["blender"]
        cleanup = settings["cleanup"]

        # Call the 'main' function in a separate thread
        run_in_thread(main, video_list, calibration, config, rotate, opensim=opensim, blender=blender,cleanup=cleanup)