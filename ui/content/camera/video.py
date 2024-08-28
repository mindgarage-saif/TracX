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
        if self.current_frame < self.start_frame:
            self.set_start_frame(self.start_frame)

        if self.end_frame != -1 and self.current_frame > self.end_frame:
            if self._video_finished_handler:
                self._video_finished_handler()
            return False, None

        ret, frame = self.video.read()
        if not ret:
            if self._video_finished_handler:
                self._video_finished_handler()
            return False, None
        self.current_frame += 1

        # Skip frames based on sample rate
        n = self.frame_rate / self.sample_rate  # Read every n-th frame
        if self.current_frame % n != 0:
            if self._frame_captured_handler:
                self._frame_captured_handler(frame, self.current_frame)

            return ret, frame

        ret, frame = self.video.read()
        self.current_frame += 1

        if not ret or (self.end_frame != -1 and self.current_frame > self.end_frame):
            if self._video_finished_handler:
                self._video_finished_handler()
            return False, None

        return ret, frame
    
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
            ret, _ = self.read()
            if not ret:
                break
            time.sleep(1 / self.sample_rate)
        self.release()

    # Signal connection methods
    def on_video_started(self, handler: Callable[[], None]):
        self._video_started_handler = handler

    def on_video_stopped(self, handler: Callable[[], None]):
        self._video_stopped_handler = handler

    def on_video_finished(self, handler: Callable[[], None]):
        self._video_finished_handler = handler

    def on_frame_captured(self, handler: Callable[[Any], None]):
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

if __name__ == "__main__":
    def on_frame_captured(frame, idx):
        print("Frame captured", idx)

    def on_video_started():
        print("Video started")

    def on_video_stopped():
        print("Video stopped")

    def on_video_finished():
        print("Video finished")

    video_capture = VideoCapture("/home/skhan/Downloads/DSV Demo Videos/SAM2 Skateboard.webm", sample_rate=24)
    video_capture.set_start_frame(100)  # Start at frame 100
    video_capture.set_end_frame(300)    # End at frame 300
    print(video_capture)

    video_capture.on_frame_captured(on_frame_captured)
    video_capture.on_video_started(on_video_started)
    video_capture.on_video_stopped(on_video_stopped)
    video_capture.on_video_finished(on_video_finished)

    video_capture.start()
