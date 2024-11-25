import os
import shutil

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QDialog, QFileDialog, QVBoxLayout

from mocap.tasks import EstimateMotionTask, VisualizeMotionTask
from mocap.ui.common import BaseTaskButton


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


class OpenSimButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__(
            "folder.png",
            VisualizeMotionTask,
            {},
            callback,
        )

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
            f"{self.task.config}-opensim",
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


class VisualizeMotionButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__("visualize.png", VisualizeMotionTask, {}, callback)

    def on_start(self):
        super().on_start()
        # TODO: Change icon

    def on_finish(self, status, result):
        super().on_finish(status, result)
        if status and result is not None:
            self.preview_video(result)

    def preview_video(self, result):
        if result is None:
            return

        dialog = QDialog()
        dialog.setWindowTitle("Motion Preview")
        dialog.setModal(True)
        dialog.setLayout(QVBoxLayout())

        video_widget = QVideoWidget()
        dialog.layout().addWidget(video_widget)

        player = QMediaPlayer()
        player.setVideoOutput(video_widget)
        player.setSource(QUrl.fromLocalFile(result))
        player.setLoops(QMediaPlayer.Loops.Infinite)
        player.play()

        # Resize the dialog, hide buttons, and show the video
        dialog.resize(800, 600)
        dialog.exec()
        player.stop()
