import os
import shutil

from PyQt6.QtWidgets import QFileDialog

from mocap.ui.tasks import VisualizeMotionTask

from .task_button import BaseTaskButton


class OpenSimButton(BaseTaskButton):
    def __init__(self, task_config, callback):
        super().__init__(
            "Get OpenSim Files",
            VisualizeMotionTask,
            task_config,
            callback,
        )

    def on_start(self):
        super().on_start()
        self.setText("Preparing...")

    def on_finish(self, status, result):
        super().on_finish(status, result)
        self.setText("Get OpenSim Files")
        if status and result is not None:
            output_dir, motion_file, model_file = result
            self.download_directory(output_dir)

    def download_directory(self, output_dir):
        # Zip the output directory
        output_dir = os.path.abspath(output_dir)
        parent_dir = os.path.dirname(output_dir)
        output_zip = os.path.join(
            parent_dir,
            f"{self.task.config.experiment_name}-opensim",
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
