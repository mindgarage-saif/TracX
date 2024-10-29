import time

import cv2
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class CameraStream(QObject):
    frame_captured = pyqtSignal(object, float)
    finished = pyqtSignal()

    def __init__(self, video_source):
        super().__init__()
        self.source = video_source
        self.video = cv2.VideoCapture(video_source)
        if not self.video.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.frame_rate = self.video.get(cv2.CAP_PROP_FPS)
        self.duration = self.video.get(cv2.CAP_PROP_FRAME_COUNT) / self.frame_rate
        self.resolution = (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self.running = False
        self.thread = QThread()
        self.moveToThread(self.thread)

        # Connect thread signals
        self.thread.started.connect(self._start_stream)
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.release)

    def start(self):
        if not self.thread.isRunning():
            self.running = True
            self.thread.start()

    def stop(self):
        self.running = False
        self.finished.emit()
        self.thread.wait()

    def _start_stream(self):
        while self.running:
            ret, frame = self.video.read()
            if not ret:
                break

            timestamp = time.time()
            self.frame_captured.emit(frame, timestamp)

            # Sleep to match the frame rate
            time.sleep(1 / self.frame_rate)

        self.finished.emit()

    def release(self):
        if self.video.isOpened():
            self.video.release()

    def __str__(self):
        info = {
            "Duration": f"{self.duration} seconds",
            "Frame Rate": self.frame_rate,
            "Resolution": f"{self.resolution[0]}x{self.resolution[1]}",
        }
        return str(info)

    def __del__(self):
        self.stop()
