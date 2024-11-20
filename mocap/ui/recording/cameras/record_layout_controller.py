from PyQt6.QtWidgets import QPushButton

from mocap.ui.common import VideoPlayerController


class RecordLayoutController(VideoPlayerController):
    def __init__(self, player, parent=None):
        super().__init__(parent, height=48)
        self.rotateLeftButton.hide()
        self.rotateRightButton.hide()
        self.player = player

        self.recordButton = QPushButton("Record", self)
        self.recordButton.setFixedSize(96, 28)
        self.showRecordButton()
        self.innerLayout.insertWidget(2, self.recordButton)

        self.play.connect(self.player.start)
        self.stop.connect(self.player.stop)
        self.recordButton.clicked.connect(self.player.toggle_record)
        self.player.recording_started.connect(self.showStopButton)
        self.player.recording_stopped.connect(self.showRecordButton)

    def showRecordButton(self):
        self.recordButton.setText("Record")
        self.recordButton.setStyleSheet("""
            QPushButton {background-color: #0e0; color: white;}
            QPushButton:hover {background-color: #0a0;}
        """)

    def showStopButton(self):
        self.recordButton.setText("Stop")
        self.recordButton.setStyleSheet("""
            QPushButton {background-color: #e00; color: white;}
            QPushButton:hover {background-color: #a00;}
        """)
