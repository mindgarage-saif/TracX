import contextlib
import os
from time import strftime

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from TracX.constants import APP_RECORDINGS
from TracX.recording.video_writer import VideoWriter


class Recorder(QObject):
    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, player):
        super().__init__()
        self.writers = {}
        self.player = player
        self.recording = False

    def init(self):
        # Clear existing writers if any
        # This also saves the videos if they are still recording
        self.reset()

        # Initialize VideoWriters
        fps = self.player.sample_rate
        for cam_id in self.player.cams:
            resolution = self.player.resolution(cam_id)
            writer = VideoWriter("", fps=fps, resolution=resolution)
            thread = QThread()
            writer.moveToThread(thread)
            thread.started.connect(writer.start_writing)
            self.writers[cam_id] = (writer, thread)

    def start(self):
        self.init()

        videos_dir = os.path.join(APP_RECORDINGS, f"VID_{strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(videos_dir, exist_ok=True)
        for cam_id, (writer, thread) in self.writers.items():
            if not thread.isRunning():
                filepath = os.path.join(videos_dir, f"CAM_{cam_id}.mp4")
                writer.filepath = filepath
                thread.start()

        self.recording = True
        self.started.emit()

    def write(self, cam_id, frame):
        if not self.recording:
            return

        if cam_id not in self.writers:
            return

        if frame is None:
            return

        writer = self.writers.get(cam_id)[0]
        writer.write_frame(frame)

    def finalize(self):
        self.recording = False
        for _, (writer, thread) in self.writers.items():
            if thread.isRunning():
                writer.stop_writing()
                thread.quit()
                thread.wait()

        self.stopped.emit()

    def reset(self):
        self.finalize()
        self.writers.clear()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.reset()
