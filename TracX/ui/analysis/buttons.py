import os
import shutil

from PyQt6.QtWidgets import QFileDialog

from TracX.tasks import EstimateMotionTask, KinematicsTask
from TracX.ui.common import BaseTaskButton
from TracX.rendering import render


class EstimateMotionButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__(None, EstimateMotionTask, None, callback)
        self.setText("Analyze")

    def on_start(self):
        super().on_start()
        # TODO: Change icon

    def on_finish(self, status, result):
        super().on_finish(status, result)
        if status:
            self.setEnabled(False)
        else:
            self.setEnabled(True)


class KinematicsButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__("folder.png",  KinematicsTask, None, callback)

    def on_start(self):
        super().on_start()
        # TODO: Change icon

    def on_finish(self, status, result):
        super().on_finish(status, result)
        if status and result is not None:
            # Render the OpenSim files
            _, motion_file, model_file = result
            render(
                osim=model_file,
                mot=motion_file,
            )
