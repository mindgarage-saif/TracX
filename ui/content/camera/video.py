import cv2
import threading
import time
from typing import Callable, Any


class VideoCapture:
    def __init__(self, video_source, sample_rate=24):
        self.video = cv2.VideoCapture(video_source)
        if not self.video.isOpened():
            raise ValueError("Unable to open video source", video_source)
        
        self.frame_rate = int(self.video.get(cv2.CAP_PROP_FPS))
        self.sample_rate = sample_rate or self.frame_rate
        self.duration = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT) / self.frame_rate)
        self.current_frame = 0
        self.start_frame = 0
        self.end_frame = -1
        self.running = False
        self.worker_thread = None
        self._last_capture_time = time.time()

        # Signal handlers
        self._video_started_handler = None
        self._video_stopped_handler = None
        self._video_finished_handler = None
        self._frame_captured_handler = None

    def set_start_frame(self, frame):
        self.start_frame = frame
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.current_frame = frame

    def set_end_frame(self, frame):
        self.end_frame = frame

    def read(self):
        ret, frame = self.video.read()

        if not ret or (self.end_frame != -1 and self.current_frame > self.end_frame):
            if self._video_finished_handler:
                self._video_finished_handler()
            return False, None, None
        
        self.current_frame += 1

        # Capture timestamp
        timestamp = self.video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Convert to seconds

        # Skip frames based on sample rate
        frame_interval = self.frame_rate / self.sample_rate
        time_since_last_capture = time.time() - self._last_capture_time

        if time_since_last_capture < 1.0 / self.sample_rate:
            return True, None, timestamp  # Skip this frame to maintain sample rate

        self._last_capture_time = time.time()

        if self._frame_captured_handler:
            self._frame_captured_handler(ret, frame, timestamp)

        return ret, frame, timestamp
    
    def release(self):
        self.video.release()

    def start(self):
        if self._video_started_handler:
            self._video_started_handler()
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.start()

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        if self._video_stopped_handler:
            self._video_stopped_handler()

    def _worker(self):
        while self.running:
            ret, frame, timestamp = self.read()
            if not ret:
                break
            time.sleep(max(0, (1 / self.sample_rate) - (time.time() - self._last_capture_time)))
        self.release()

    # Signal connection methods
    def on_video_started(self, handler: Callable[[], None]):
        self._video_started_handler = handler

    def on_video_stopped(self, handler: Callable[[], None]):
        self._video_stopped_handler = handler

    def on_video_finished(self, handler: Callable[[], None]):
        self._video_finished_handler = handler

    def on_frame_captured(self, handler: Callable[[Any, Any], None]):
        self._frame_captured_handler = handler

    def __str__(self):
        info = {
            "Duration": f"{self.duration} seconds",
            "Frame Rate": self.frame_rate,
            "Sample Rate": self.sample_rate,
            "Start Frame": self.start_frame,
            "End Frame": self.end_frame
        }
        return str(info)
