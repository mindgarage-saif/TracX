# controller_widget.py

import logging
import os
from time import strftime
from typing import Any

from PyQt6.QtCore import Qt, QThread, pyqtSlot
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..constants import APP_RECORDINGS
from .camera_streams import CameraStreams
from .stream_processor import StreamProcessor
from .video_writer import VideoWriter

logger = logging.getLogger(__name__)


class ControllerWidget(QWidget):
    """
    Main controller widget that manages camera streams, processing, and video writing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = None
        self._camera_id = None
        self._sources = []
        self.on_camera_changed = lambda: None
        self.on_frame_fn = lambda frame: None

        self.init_ui()

        # Initialize components
        self.stream_processor = StreamProcessor()
        self.video_writers = {}  # key: camera_id, value: VideoWriter instance

        # Setup threads
        self.camera_thread = QThread()
        self.processor_thread = QThread()
        self.writer_threads = {}  # key: camera_id, value: QThread

        # Connect signals and slots
        self.stream_processor.processed_frames.connect(self.handle_processed_frames)
        self.stream_processor.error_occurred.connect(self.handle_error)

        # Start threads
        self.camera_thread.start()
        self.processor_thread.start()

    def add_source(self, camera_id: int, view: Any):
        self._sources.append((camera_id, view))

    def initialize(self):
        camera_id = [c[0] for c in self._sources]
        logger.info(f"Changing camera to {camera_id}")

        camera_views = [c[1] for c in self._sources]
        for view in camera_views:
            view.clear()
            view.flip = True

        assert all(isinstance(c, int) or c.isdigit() for c in camera_id)
        self._camera_id = camera_id

        self._camera = CameraStreams(self._sources)
        self.camera_thread.started.connect(self._camera.start)
        self._camera.frames_captured.connect(self.stream_processor.process_frames)
        self._camera.error_occurred.connect(self.handle_error)

        # Move workers to threads
        self._camera.moveToThread(self.camera_thread)
        self.stream_processor.moveToThread(self.processor_thread)

    def init_ui(self):
        """
        Initializes the UI components.
        """
        self.start_button = QPushButton("Start Capture")
        self.start_button.clicked.connect(self.toggle_capture)

        self.stop_button = QPushButton("Stop Capture")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video display labels for each camera
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    @pyqtSlot()
    def toggle_capture(self):
        """
        Toggles the capture state.
        """
        if self._camera.running:
            self.stop_capture()
        else:
            self.start_capture()

    @pyqtSlot()
    def start_capture(self):
        """
        Starts the capture process, including initializing VideoWriters.
        """
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Running")

        # Initialize VideoWriters
        videos_dir = os.path.join(APP_RECORDINGS, f"VID_{strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(videos_dir, exist_ok=True)

        for cam_id, view in self._camera.sources:
            filepath = os.path.join(videos_dir, f"camera_{cam_id}.mp4")
            writer = VideoWriter(
                filepath,
                fps=self._camera.sample_rate,
                resolution=self._camera.resolution(cam_id),
            )
            writer_thread = QThread()
            writer.moveToThread(writer_thread)
            writer_thread.started.connect(writer.start_writing)

            def write_frames(frames):
                for (cam_id, view), frame in zip(self._camera.sources, frames):
                    if frame is not None:
                        self.write_frame(cam_id, frame)

            self.stream_processor.processed_frames.connect(write_frames)
            writer_thread.start()

            self.video_writers[cam_id] = (writer, writer_thread)

        # Start CameraStreams
        self._camera.start()
        self.stream_processor.start_processing()

    @pyqtSlot()
    def stop_capture(self):
        """
        Stops the capture process and cleans up resources.
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Stopped")

        # Stop CameraStreams
        self._camera.stop()

        # Stop StreamProcessor
        self.stream_processor.stop_processing()

        # Stop VideoWriters
        for cam_id, (writer, thread) in self.video_writers.items():
            writer.stop_writing()
            thread.quit()
            thread.wait()
        self.video_writers.clear()

    @pyqtSlot(list)
    def handle_processed_frames(self, frames: list):
        """
        Handles frames after processing.

        Args:
            frames (list): List of processed frames from all cameras.
        """
        for (cam_id, view), frame in zip(self._camera.sources, frames):
            if frame is not None:
                view.show(frame)

    def write_frame(self, cam_id: int, frame: Any):
        """
        Writes a frame to the corresponding VideoWriter.

        Args:
            cam_id (int): The camera ID.
            frame (Any): The processed frame to write.
        """
        writer, _ = self.video_writers.get(cam_id, (None, None))
        if writer:
            writer.write_frame(frame)

    @pyqtSlot(str)
    def handle_error(self, error_message: str):
        """
        Handles errors emitted from any component.

        Args:
            error_message (str): The error message.
        """
        logger.error(error_message)
        self.status_label.setText(f"Error: {error_message}")

    def closeEvent(self, event):
        """
        Handles the widget close event to ensure proper cleanup.
        """
        self.stop_capture()

        # Stop StreamProcessor thread
        self.processor_thread.quit()
        self.processor_thread.wait()

        # Stop CameraStreams thread
        self.camera_thread.quit()
        self.camera_thread.wait()

        event.accept()

    def release(self):
        if self._camera is not None:
            self._camera.release()
            self._camera = None

            for view in [c[1] for c in self._sources]:
                view.clear()
