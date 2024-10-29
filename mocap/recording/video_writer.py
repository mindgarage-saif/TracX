import logging

import cv2
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)


class VideoWriter(QObject):
    """
    Writes frames to a video file.
    """

    error_occurred = pyqtSignal(str)

    def __init__(self, filepath: str, fps: float, resolution: tuple):
        super().__init__()
        self.filepath = filepath
        self.fps = fps
        self.resolution = resolution
        self._is_running = False
        self.writer = None

    @pyqtSlot()
    def start_writing(self):
        """
        Initializes the video writer.
        """
        try:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.writer = cv2.VideoWriter(
                self.filepath, fourcc, self.fps, self.resolution
            )
            if not self.writer.isOpened():
                raise ValueError(
                    f"Unable to open video writer for file {self.filepath}"
                )
            self._is_running = True
            logger.info(f"Started writing to {self.filepath}")
        except Exception as e:
            self.error_occurred.emit(str(e))

    @pyqtSlot(object)
    def write_frame(self, frame):
        """
        Writes a single frame to the video file.

        Args:
            frame (numpy.ndarray): The processed frame to write.
        """
        if not self._is_running or self.writer is None:
            return

        try:
            self.writer.write(frame)
        except Exception as e:
            self.error_occurred.emit(str(e))

    @pyqtSlot()
    def stop_writing(self):
        """
        Releases the video writer.
        """
        if self.writer:
            self.writer.release()
            self.writer = None
            self._is_running = False
            logger.info(f"Stopped writing to {self.filepath}")
