import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .camera_stream import CameraStream


def get_recommended_fps(frame_rates):
    """
    Returns the maximum even number less than or equal to the smallest frame rate in the list.

    Args:
        frame_rates (List[int]): A list of frame rates from different cameras.

    Returns:
        int: The recommended frame rate.

    Raises:
        ValueError: If the input list is empty or contains non-integer values.
    """
    if not frame_rates:
        raise ValueError("The frame_rates list is empty.")

    if not all(isinstance(fps, int) for fps in frame_rates):
        raise ValueError("All frame rates must be integers.")

    smallest_fps = min(frame_rates)

    # Find the maximum even number <= smallest_fps
    if smallest_fps % 2 == 0:
        recommended_fps = smallest_fps
    else:
        recommended_fps = smallest_fps - 1

    if recommended_fps < 1:
        raise ValueError("No valid even frame rate found.")

    return recommended_fps


class CameraStreams:
    def __init__(
        self,
        sources: Union[int, List[int], Tuple[int]] = 0,
        sample_rate: Optional[float] = None,
        sync_delta: Optional[float] = None,
    ):
        """
        Initialize synchronized capture for multiple cameras.

        Args:
            sources (Union[int, List[int], Tuple[int]]): Camera source IDs.
            sample_rate (float): Desired sample rate in frames per second.
            sync_delta (float): Maximum allowed time difference between frames for synchronization.
        """
        # Normalize sources to a list
        if isinstance(sources, int):
            sources = [sources]
        elif isinstance(sources, tuple):
            sources = list(sources)
        elif not isinstance(sources, list):
            raise ValueError("Sources must be an int, list, or tuple of ints.")

        if sample_rate is None:
            sample_rate = get_recommended_fps(
                [CameraStream(s).frame_rate for s in sources]
            )

        self.sources = sources
        self.sample_rate = sample_rate

        # Determine sync_delta if not provided
        if sync_delta is None:
            # Define sync_delta as half of the frame period
            frame_period = 1.0 / self.sample_rate
            self.sync_delta = frame_period / 2
        else:
            self.sync_delta = sync_delta

        # Initialize VideoCapture instances for each source
        self.cams: Dict[int, CameraStream] = {
            s: CameraStream(s, sample_rate) for s in sources
        }

        # Buffers to store frames from each camera
        self.buffers: Dict[int, List[Tuple[float, Any]]] = {s: [] for s in sources}

        # Flags and counters
        self.capture_frames = True
        self.running = False

        # Synchronization primitives
        self.lock = threading.Lock()
        self.sync_condition = threading.Condition(self.lock)

        # Signal handlers
        self._video_started_handler = None
        self._video_stopped_handler = None
        self._video_finished_handler = None
        self._frame_captured_handler = None

    # Signal connection methods
    def on_start(self, handler: Callable[[], None]):
        self._video_started_handler = handler

    def on_stop(self, handler: Callable[[], None]):
        self._video_stopped_handler = handler

    def on_finish(self, handler: Callable[[], None]):
        self._video_finished_handler = handler

    def on_frame(self, handler: Callable[[Dict[int, Any]], None]):
        """
        Handler receives a dictionary mapping camera IDs to frames.

        Args:
            handler (Callable[[Dict[int, Any]], None]): Function to handle synchronized frames.
        """
        self._frame_captured_handler = handler

    def resolution(self, cam_id):
        for idx, cam in self.cams.items():
            if idx == cam_id:
                return cam.resolution
        return (640, 480)

    def start_capture(self):
        # Register event handlers for each camera
        for cam_id, cam in self.cams.items():
            cam.on_frame(
                lambda ret, frame, timestamp, cam_id=cam_id: self._on_captured_frame(
                    ret, frame, timestamp, cam_id
                )
            )

        # Call the video started handler
        if self._video_started_handler:
            self._video_started_handler()

        # Start all cameras
        for cam in self.cams.values():
            cam.start()

    def stop_capture(self):
        # Stop all cameras
        for cam in self.cams.values():
            cam.stop()

        # Call the video stopped handler
        if self._video_stopped_handler:
            self._video_stopped_handler()

        # Call the video finished handler
        if self._video_finished_handler:
            self._video_finished_handler()

    def _on_captured_frame(self, ret: bool, frame: Any, timestamp: float, cam_id: int):
        with self.sync_condition:
            if not self.capture_frames:
                return

            if ret and frame is not None:
                self.buffers[cam_id].append((timestamp, frame))
                self._check_sync()

    def _check_sync(self):
        """
        Attempt to synchronize frames from all cameras.
        """
        while self.capture_frames and all(
            len(buffer) > 0 for buffer in self.buffers.values()
        ):
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

                # Invoke the frame captured handler
                if self._frame_captured_handler:
                    self._frame_captured_handler(synchronized_frames)
            else:
                # Find cameras that are behind the target_time
                for cam_id, (timestamp, _) in current_frames.items():
                    if timestamp < target_time - self.sync_delta:
                        # Discard the outdated frame
                        self.buffers[cam_id].pop(0)

                # If any buffer was updated, re-evaluate synchronization
                # This ensures that the loop continues if synchronization can now be achieved
                continue

            # Notify the worker thread
            self.sync_condition.notify_all()

    def start(self):
        """
        Start the synchronized capture in a separate thread.
        """
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()

    def _worker(self):
        """
        Worker thread to manage the capture process.
        """
        self.start_capture()
        with self.sync_condition:
            while self.capture_frames:
                self.sync_condition.wait()  # Wait until notified by _check_sync
        self.stop_capture()

    def release(self):
        """
        Release all resources.
        """
        for cam in self.cams.values():
            cam.release()