import contextlib
import logging
import os
import time

import cv2
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class VideoPlayer(QObject):
    frame = pyqtSignal(object)
    timed_frame = pyqtSignal(object, float)
    progress = pyqtSignal(float, float)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._source = None
        self._video = None

        # Video metadata
        self.frame_rate = -1
        self.duration = 1
        self.resolution = (0, 0)

        # Lifecycle flags
        self.running = False
        self.paused = False

        # Settings
        self.loop = True

        # Create a thread to run the video stream
        self.thread = QThread()
        self.moveToThread(self.thread)

    @property
    def isWebcam(self):
        return isinstance(self._source, int)

    def setSource(self, source):
        # Check that source is a valid video file
        if isinstance(source, str) and not os.path.exists(source):
            raise ValueError("Video source does not exist", source)

        # Open the video source
        self._source = source
        self._video = cv2.VideoCapture(source)

        # Check that the video source was opened
        if not self._video.isOpened():
            raise ValueError("Unable to open video source", source)

        # Show the first frame
        ret, frame = self._video.read()
        if ret:
            self.frame.emit(frame)

        # Update metadata
        self.updateMetadata()

        # Reset lifecycle flags
        self.running = False
        self.paused = False

        # Relase the source
        self._video.release()

    def updateMetadata(self):
        self.frame_rate = self._video.get(cv2.CAP_PROP_FPS)
        self.duration = self._video.get(cv2.CAP_PROP_FRAME_COUNT) / self.frame_rate
        self.resolution = (
            int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def start(self):
        if self.running or self._source is None:
            return

        # Acquire the source
        self._video = cv2.VideoCapture(self._source)

        # Connect thread signals
        self.thread.started.connect(self._start_stream)

        # Start the thread
        self.running = True

        if not self.thread.isRunning():
            self.thread.start()
        else:
            self.thread.quit()
            self.thread.wait()
            self.thread.start()

    def stop(self):
        if not self.running or self._video is None:
            return

        # Reset lifecycle flags
        self.running = False
        self.paused = False

        # Emit the finished signal
        self.finished.emit()

        # Reset the video preview
        if self.isWebcam and self._video.isOpened():
            self._video.release()
        else:
            self._video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._video.read()
            if ret:
                if self.isWebcam:
                    self.frame.emit(cv2.flip(frame, 1))
                else:
                    self.frame.emit(frame)

        logging.debug("Video player stopped for source: %s", self._source)

    def pause(self):
        self.paused = True

    def resume(self):
        if not self.running:
            self.start()
            return

        self.paused = False

    def emit(self, frame):
        # Emit the frame signal on the main thread
        logging.debug("Emitting frame from source: %s", self._source)
        self.frame.emit(frame)
        self.timed_frame.emit(frame, time.time())

    def _start_stream(self):
        logging.debug("Video player started for source: %s", self._source)
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = self._video.read()
            if not ret:
                if self.loop:
                    self._video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
                    continue
                break

            self.emit(frame)

            # Emit the progress signal
            if not self.isWebcam:
                current_time = self._video.get(cv2.CAP_PROP_POS_MSEC) / 1000
                self.progress.emit(current_time, current_time / self.duration)

                # Sleep to match the frame rate
                time.sleep(1 / self.frame_rate)
        logging.debug("Video player finished for source: %s", self._source)

        self.stop()

    def release(self):
        if self._video.isOpened():
            self._video.release()

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.release()
