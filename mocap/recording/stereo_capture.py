import threading
import time
from typing import Any, Callable

from .video import VideoCapture


class StereoCapture:
    def __init__(
        self,
        camera1_source: dict = 0,
        camera2_source: dict = 1,
        sample_rate=24,
        max_frames=100,
    ):
        # Initialize video capture for both cameras
        self.cam1 = VideoCapture(camera1_source, sample_rate)
        self.cam2 = VideoCapture(camera2_source, sample_rate)

        # Store the frames captured from both cameras with timestamps
        self.buffer1 = []
        self.buffer2 = []

        # Max frames to capture for calibration
        self.max_frames = max_frames

        # Flag to control synchronization and capturing
        self.capture_frames = True
        self.frame_count = 0

        # Synchronization lock and condition
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

    def on_frame_captured(self, handler: Callable[[Any, Any], None]):
        self._frame_captured_handler = handler

    def start_capture(self):
        # Register event handlers
        self.cam1.on_frame_captured(self._on_captured_frame1)
        self.cam2.on_frame_captured(self._on_captured_frame2)

        # Call the video started handler
        if self._video_started_handler:
            self._video_started_handler()

        # Start both cameras
        self.cam1.start()
        self.cam2.start()

    def stop_capture(self):
        # Stop both cameras
        self.cam1.stop()
        self.cam2.stop()

        # Call the video stopped handler
        if self._video_stopped_handler:
            self._video_stopped_handler()

        # Call the video finished handler
        if self._video_finished_handler:
            self._video_finished_handler()

    def _on_captured_frame1(self, ret, frame, timestamp):
        with self.sync_condition:
            if self.capture_frames:
                self.buffer1.append((timestamp, frame))
                self._check_sync()

    def _on_captured_frame2(self, ret, frame, timestamp):
        with self.sync_condition:
            if self.capture_frames:
                self.buffer2.append((timestamp, frame))
                self._check_sync()

    def _check_sync(self):
        # Ensure both frames are captured before saving
        if len(self.buffer1) > 0 and len(self.buffer2) > 0:
            # Get the earliest frames by timestamp
            time1, frame1 = self.buffer1[0]
            time2, frame2 = self.buffer2[0]

            # Check for closest matching timestamps
            if abs(time1 - time2) <= 1 / self.cam1.sample_rate:  # Allow a small delta
                self.buffer1.pop(0)
                self.buffer2.pop(0)
                # Call the frame captured handler
                if self._frame_captured_handler:
                    self._frame_captured_handler(frame1, frame2)
                # Increment frame count and save the synchronized frames
                self.frame_count += 1

                # Check if max frames limit is reached
                if self.max_frames != -1 and self.frame_count >= self.max_frames:
                    self.capture_frames = False
                    self.stop_capture()
            elif time1 < time2:
                # Camera 1 is ahead; remove its frame
                self.buffer1.pop(0)
            else:
                # Camera 2 is ahead; remove its frame
                self.buffer2.pop(0)

            # Notify all threads waiting on this condition
            self.sync_condition.notify_all()

    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.start()

    def _worker(self):
        self.start_capture()
        while self.capture_frames:
            with self.sync_condition:
                self.sync_condition.wait()  # Wait for synchronized frame capture
        self.stop_capture()

    def release(self):
        self.cam1.release()
        self.cam2.release()
