import threading
from typing import Any, Callable, List, Tuple, Union, Dict
import time

from .video import VideoCapture  # Ensure this import is correct based on your project structure


class SynchronizedCapture:
    def __init__(
        self,
        sources: Union[int, List[int], Tuple[int]] = 0,
        sample_rate: float = 24.0,
        max_frames: int = 100,
        sync_delta: float = 0.05  # Maximum allowed time difference in seconds
    ):
        """
        Initialize synchronized capture for multiple cameras.

        Args:
            sources (Union[int, List[int], Tuple[int]]): Camera source IDs.
            sample_rate (float): Desired sample rate in frames per second.
            max_frames (int): Maximum number of synchronized frames to capture.
            sync_delta (float): Maximum allowed time difference between frames for synchronization.
        """
        # Normalize sources to a list
        if isinstance(sources, int):
            sources = [sources]
        elif isinstance(sources, tuple):
            sources = list(sources)
        elif not isinstance(sources, list):
            raise ValueError("Sources must be an int, list, or tuple of ints.")

        self.sources = sources
        self.sample_rate = sample_rate
        self.max_frames = max_frames
        self.sync_delta = sync_delta

        # Initialize VideoCapture instances for each source
        self.cams: Dict[int, VideoCapture] = {s: VideoCapture(s, sample_rate) for s in sources}

        # Buffers to store frames from each camera
        self.buffers: Dict[int, List[Tuple[float, Any]]] = {s: [] for s in sources}

        # Flags and counters
        self.capture_frames = True
        self.frame_count = 0
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
    def on_video_started(self, handler: Callable[[], None]):
        self._video_started_handler = handler

    def on_video_stopped(self, handler: Callable[[], None]):
        self._video_stopped_handler = handler

    def on_video_finished(self, handler: Callable[[], None]):
        self._video_finished_handler = handler

    def on_frame_captured(self, handler: Callable[[Dict[int, Any]], None]):
        """
        Handler receives a dictionary mapping camera IDs to frames.

        Args:
            handler (Callable[[Dict[int, Any]], None]): Function to handle synchronized frames.
        """
        self._frame_captured_handler = handler

    def start_capture(self):
        # Register event handlers for each camera
        for cam_id, cam in self.cams.items():
            cam.on_frame_captured(
                lambda ret, frame, timestamp, cam_id=cam_id: self._on_captured_frame(ret, frame, timestamp, cam_id)
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
        while self.capture_frames and all(len(buffer) > 0 for buffer in self.buffers.values()):
            # Extract the earliest timestamp from each buffer
            current_frames = {cam_id: buffer[0] for cam_id, buffer in self.buffers.items()}

            # Find the maximum of the earliest timestamps
            target_time = max(frame[0] for frame in current_frames.values())

            # Check if all frames are within sync_delta of the target_time
            if all(abs(frame[0] - target_time) <= self.sync_delta for frame in current_frames.values()):
                # All frames are synchronized
                synchronized_frames = [buffer.pop(0)[1] for buffer in self.buffers.values()]

                # Invoke the frame captured handler
                if self._frame_captured_handler:
                    self._frame_captured_handler(synchronized_frames)

                # Increment frame count
                self.frame_count += 1

                # Check if max frames limit is reached
                if self.max_frames != -1 and self.frame_count >= self.max_frames:
                    self.capture_frames = False
                    self.stop_capture()
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


# Example Usage
if __name__ == "__main__":
    def on_frame_captured(frames: Dict[int, Any]):
        """
        Handle synchronized frames from all cameras.

        Args:
            frames (Dict[int, Any]): Dictionary mapping camera IDs to frames.
        """
        print(f"Synchronized Frame {synchronized_capture.frame_count}:")
        for cam_id, frame in frames.items():
            print(f"  Camera {cam_id}: Frame size {frame.shape}")

    def on_video_started():
        print("Video capture started.")

    def on_video_stopped():
        print("Video capture stopped.")

    def on_video_finished():
        print("Video capture finished.")

    # Initialize SynchronizedCapture with multiple camera sources
    synchronized_capture = SynchronizedCapture(
        sources=[0, 1, 2],  # Replace with your actual camera indices or video files
        sample_rate=24.0,
        max_frames=200,
        sync_delta=0.05  # 50 milliseconds tolerance
    )

    # Connect signal handlers
    synchronized_capture.on_frame_captured(on_frame_captured)
    synchronized_capture.on_video_started(on_video_started)
    synchronized_capture.on_video_stopped(on_video_stopped)
    synchronized_capture.on_video_finished(on_video_finished)

    # Start the synchronized capture
    synchronized_capture.start()

    # Keep the main thread alive until capture is complete
    try:
        while synchronized_capture.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user. Stopping capture...")
        synchronized_capture.capture_frames = False
        synchronized_capture.stop_capture()
