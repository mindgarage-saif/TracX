import threading
from typing import Any, Dict, List, Optional, Tuple, Union

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from .camera_stream import CameraStream


class CameraStreams(QObject):
    """
    Captures frames from multiple cameras and emits synchronized frames.
    """

    frames_captured = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        sources: Union[int, List[int], Tuple[int]],
        sync_delta: Optional[float] = None,
    ):
        super().__init__()

        self.sources = sources
        # Initialize CameraStream instances for each source
        try:
            self.cams: Dict[int, CameraStream] = {
                s[0]: CameraStream(s[0]) for s in sources
            }

            # All cameras should have the same frame rate
            frame_rate = self.cams[sources[0][0]].frame_rate
            if not all(cam.frame_rate == frame_rate for cam in self.cams.values()):
                raise ValueError("All cameras must have the same frame rate")

            self.sample_rate = frame_rate
        except ValueError as e:
            self.error_occurred.emit(str(e))
            self.cams = {}

        # Determine sync_delta if not provided
        if sync_delta is None:
            # Define sync_delta as half of the frame period
            frame_period = 1.0 / self.sample_rate
            self.sync_delta = frame_period / 2
        else:
            self.sync_delta = sync_delta

        # Buffers to store frames from each camera
        self.buffers: Dict[int, List[Tuple[float, Any]]] = {s[0]: [] for s in sources}

        # Flags
        self.running = False

        # Synchronization primitives
        self.lock = threading.Lock()
        self.sync_condition = threading.Condition(self.lock)

        # Connect camera frame signals to the handler
        for cam_id, cam in self.cams.items():
            cam.frame_captured.connect(
                lambda frame, timestamp, cid=cam_id: self.on_captured_frame(
                    frame, timestamp, cid
                )
            )

    def resolution(self, cam_id: int) -> Tuple[int, int]:
        """
        Returns the resolution of the camera with the given ID.
        """
        return self.cams[cam_id].resolution

    @pyqtSlot()
    def start(self):
        """
        Starts all camera streams.
        """
        if self.running:
            return
        self.running = True
        for cam in self.cams.values():
            cam.start()

    @pyqtSlot()
    def stop(self):
        """
        Stops all camera streams.
        """
        if not self.running:
            return
        self.running = False
        for cam in self.cams.values():
            cam.stop()

    @pyqtSlot(object, float, int)
    def on_captured_frame(self, frame: Any, timestamp: float, cam_id: int):
        """
        Handles frames captured from individual cameras.
        """
        with self.sync_condition:
            if not self.running:
                return

            if frame is not None:
                self.buffers[cam_id].append((timestamp, frame))
                self.check_sync()

    def check_sync(self):
        """
        Attempts to synchronize frames from all cameras.
        """
        while self.running and all(len(buffer) > 0 for buffer in self.buffers.values()):
            # Extract the earliest timestamp from each buffer
            current_frames = {
                cam_id: buffer[0] for cam_id, buffer in self.buffers.items()
            }

            # Find the maximum of the earliest timestamps
            target_time = max(frame[0] for frame in current_frames.values())

            # Check if all frames are within sync_delta of the target_time
            if all(
                abs(frame[0] - target_time) <= self.sync_delta
                for frame in current_frames.values()
            ):
                # All frames are synchronized
                synchronized_frames = [
                    buffer.pop(0)[1] for buffer in self.buffers.values()
                ]

                self.frames_captured.emit(synchronized_frames)
            else:
                # Discard outdated frames
                for cam_id, (timestamp, _) in current_frames.items():
                    if timestamp < target_time - self.sync_delta:
                        self.buffers[cam_id].pop(0)
                # Continue checking in case synchronization is now possible

    def release(self):
        """
        Releases all camera resources.
        """
        for cam in self.cams.values():
            cam.release()
