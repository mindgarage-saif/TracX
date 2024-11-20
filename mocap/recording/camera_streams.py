import contextlib
import logging
import threading
from typing import Any, List, Optional, Tuple, Union

from PyQt6.QtCore import QObject, pyqtSignal

from .video_player import VideoPlayer


class CameraStreams(QObject):
    """
    Captures frames from multiple cameras and emits synchronized frames.
    """

    frames_captured = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cams = {}
        self.sync_delta = None

        # Flags
        self.running = False

        # Synchronization primitives
        self.lock = threading.Lock()
        self.sync_condition = threading.Condition(self.lock)

    def setSources(
        self,
        sources: Union[int, List[int], Tuple[int]],
        sync_delta: Optional[float] = None,
    ):
        """
        Initialize camera sources and synchronization settings.
        """
        self.cams = {}

        for s in sources:
            stream = VideoPlayer()
            stream.setSource(s)
            self.cams[s] = stream

        # Ensure all cameras have the same frame rate
        frame_rate = self.cams[sources[0]].frame_rate
        if not all(cam.frame_rate == frame_rate for cam in self.cams.values()):
            raise ValueError("All cameras must have the same frame rate")

        self.sample_rate = frame_rate

        # Define sync_delta if not provided
        if sync_delta is None:
            frame_period = 1.0 / self.sample_rate
            self.sync_delta = frame_period / 2
        else:
            self.sync_delta = sync_delta

        # Initialize frame buffers
        self.buffers = {s: [] for s in sources}

        # Connect signals with explicit binding to avoid reference issues
        for cam_id, cam in self.cams.items():
            cam.timed_frame.connect(
                lambda frame, timestamp, cam_id=cam_id: self.handle_frame(
                    frame, timestamp, cam_id
                )
            )

    def resolution(self, cam_id: int) -> Tuple[int, int]:
        """
        Get the resolution of a camera.
        """
        return self.cams[cam_id].resolution

    def handle_frame(self, frame: Any, timestamp: float, cam_id: int):
        """
        Handle frames received from individual cameras.
        """
        with self.sync_condition:
            if not self.running:
                return

            logging.debug(f"Received frame from camera {cam_id} at {timestamp}")
            self.buffers[cam_id].append((timestamp, frame))
            self.check_sync()

    def check_sync(self):
        """
        Synchronize frames across all cameras.
        """
        while self.running and all(len(buffer) > 0 for buffer in self.buffers.values()):
            current_frames = {
                cam_id: buffer[0] for cam_id, buffer in self.buffers.items()
            }
            target_time = max(frame[0] for frame in current_frames.values())

            if all(
                abs(frame[0] - target_time) <= self.sync_delta
                for frame in current_frames.values()
            ):
                synchronized_frames = [
                    self.buffers[cam_id].pop(0)[1] for cam_id in self.buffers
                ]
                self.frames_captured.emit(synchronized_frames)
                logging.debug("Synchronized frames emitted")
            else:
                for cam_id, (timestamp, _) in current_frames.items():
                    if timestamp < target_time - self.sync_delta:
                        self.buffers[cam_id].pop(0)
                        logging.warning(f"Dropped frame from camera {cam_id}")

    def start(self):
        """
        Start capturing from all cameras.
        """
        if self.running:
            return

        self.running = True
        for cam in self.cams.values():
            cam.start()

    def stop(self):
        """
        Stop capturing from all cameras.
        """
        if not self.running:
            return

        self.running = False
        for cam in self.cams.values():
            cam.stop()

    def release(self):
        """
        Release all camera resources.
        """
        for cam in self.cams.values():
            cam.release()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.release()
