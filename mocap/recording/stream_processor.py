from typing import Any, List

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class StreamProcessor(QObject):
    """
    Processes frames received from multiple cameras.
    """

    processed_frames = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = False

    @pyqtSlot()
    def start_processing(self):
        """
        Slot to start processing. Can be expanded if needed.
        """
        self._is_running = True
        # Any initialization if required

    @pyqtSlot(list)
    def process_frames(self, frames: List[Any]):
        """
        Processes incoming frames and emits the processed frames.

        Args:
            frames (List[Any]): List of frames from multiple cameras.
        """
        if not self._is_running:
            return

        try:
            # Example processing: center crop to 16:9 aspect ratio
            # processed = [self.center_crop(frame, 16 / 9) for frame in frames]
            processed = [frame for frame in frames]
            self.processed_frames.emit(processed)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def center_crop(self, frame, target_aspect_ratio=16 / 9):
        """
        Crops the input frame to the target aspect ratio centered.

        Args:
            frame (numpy.ndarray): The input image frame.
            target_aspect_ratio (float): The desired aspect ratio (width / height).

        Returns:
            numpy.ndarray: The center-cropped frame.
        """
        height, width = frame.shape[:2]
        current_aspect_ratio = width / height

        if current_aspect_ratio > target_aspect_ratio:
            # Crop width
            new_width = int(height * target_aspect_ratio)
            start_x = (width - new_width) // 2
            cropped_frame = frame[:, start_x : start_x + new_width]
        else:
            # Crop height
            new_height = int(width / target_aspect_ratio)
            start_y = (height - new_height) // 2
            cropped_frame = frame[start_y : start_y + new_height, :]

        return cropped_frame

    @pyqtSlot()
    def stop_processing(self):
        """
        Slot to stop processing.
        """
        self._is_running = False
