import os
import shutil

from PyQt6.QtWidgets import QFileDialog

from TracX.tasks import EstimateMotionTask, KinematicsTask
from TracX.ui.common import BaseTaskButton


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
            output_dir, motion_file, model_file = result
            self.download_directory(output_dir)

    def download_directory(self, output_dir):
        # Zip the output directory
        output_dir = os.path.abspath(output_dir)
        parent_dir = os.path.dirname(output_dir)
        output_zip = os.path.join(
            parent_dir,
            f"{self.task.experiment}-opensim",
        )
        shutil.make_archive(output_zip, "zip", output_dir)

        # Open a file dialog to save the zip file
        output_zip += ".zip"
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.selectFile(os.path.basename(output_zip))

        if file_dialog.exec():
            save_path = file_dialog.selectedFiles()[0]
            if save_path:
                shutil.move(output_zip, save_path)
                # TOOD: Show a success message
                print(f"Saved OpenSim files to {save_path}")
