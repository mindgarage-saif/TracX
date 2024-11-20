import contextlib
import logging

import cv2
from PyQt6.QtCore import QThread, pyqtSignal

from mocap.recording.camera_streams import CameraStreams
from mocap.recording.stream_processor import StreamProcessor

from .recorder import Recorder

logger = logging.getLogger(__name__)


class SynchronizedVideoPlayer(CameraStreams):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sources = []

        # Create recorder
        self.recorder = Recorder(self)
        self.recorder.started.connect(self.recording_started.emit)
        self.recorder.stopped.connect(self.recording_stopped.emit)

        # Create processor
        self.processor = StreamProcessor()
        self.processor_thread = QThread()
        self.processor_thread.started.connect(self.processor.start_processing)
        self.processor_thread.finished.connect(self.processor.stop_processing)
        self.processor.moveToThread(self.processor_thread)

        # Connect signals and slots
        self.processor.processed_frames.connect(self.show_frames)
        self.processor.error_occurred.connect(self.show_error)

        self.frames_captured.connect(self.processor.process_frames)

    def setSources(self, sources):
        super().setSources([s[0] for s in sources])
        self.sources.clear()
        for source, view in sources:
            self.sources.append((source, view))

    def start(self):
        """
        Starts the capture process, including initializing VideoWriters.
        """
        super().start()
        if self.running:
            self.processor_thread.start()

    def toggle_record(self):
        if self.recorder.recording:
            self.recorder.finalize()
        else:
            self.recorder.start()

        return self.recorder.recording

    def drawRecordingOverlay(self, frame):
        h, w, _ = frame.shape
        cv2.line(
            frame,
            (int(w * 0.025), int(h * 0.025)),
            (int(w * 0.1), int(h * 0.025)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.025), int(h * 0.025)),
            (int(w * 0.025), int(h * 0.1)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.975), int(h * 0.025)),
            (int(w * 0.9), int(h * 0.025)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.975), int(h * 0.025)),
            (int(w * 0.975), int(h * 0.1)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.025), int(h * 0.975)),
            (int(w * 0.1), int(h * 0.975)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.025), int(h * 0.975)),
            (int(w * 0.025), int(h * 0.9)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.975), int(h * 0.975)),
            (int(w * 0.9), int(h * 0.975)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.line(
            frame,
            (int(w * 0.975), int(h * 0.975)),
            (int(w * 0.975), int(h * 0.9)),
            (255, 255, 255),
            int(w * 0.005),
        )
        cv2.circle(frame, (int(w * 0.05), int(h * 0.065)), 5, (0, 0, 255), -1)
        cv2.putText(
            frame,
            "REC",
            (int(w * 0.07), int(h * 0.075)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    def show_frames(self, frames: list):
        """
        Handles frames after processing.

        Args:
            frames (list): List of processed frames from all cameras.
        """
        for (cam_id, view), frame in zip(self.sources, frames):
            if frame is not None:
                if self.recorder.recording:
                    self.recorder.write(cam_id, frame)
                    self.drawRecordingOverlay(frame)

                # Show preview
                view.showFrame(frame)

    def show_error(self, error_message: str):
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
        self.stop()

        # Stop StreamProcessor thread
        self.processor_thread.quit()
        self.processor_thread.wait()

        event.accept()

    def release(self):
        super().release()
        self.recorder.reset()

        for _, view in self.sources:
            view.clear()

        if self.processor_thread.isRunning():
            self.processor_thread.quit()
            self.processor_thread.wait()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.release()
