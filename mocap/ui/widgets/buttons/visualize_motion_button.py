from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from mocap.ui.tasks import VisualizeMotionTask

from .task_button import BaseTaskButton


class VisualizeMotionButton(BaseTaskButton):
    def __init__(self, task_config, callback):
        super().__init__("Preview Motion", VisualizeMotionTask, task_config, callback)

    def on_start(self):
        super().on_start()
        self.setText("Preparing...")

    def on_finish(self, status, result):
        super().on_finish(status, result)
        self.setText("Preview Motion")
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
