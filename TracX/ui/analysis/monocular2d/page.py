import asyncio
import logging
import os
import shutil
import threading
import time

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from TracX.constants import FEATURE_STREAMING_ENABLED
from TracX.core import Experiment
from TracX.core.analyze2d import process_frame, setup_pose_tracker
from TracX.streaming import MotionDataStreamer
from TracX.ui.styles import PAD_Y

from .data_widget import ExperimentDataWidget
from .settings import Monocular2DSettingsPanel


class Monocular2DAnalysisPage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Experiment data
        self.experiment = None
        self.data = ExperimentDataWidget(self)
        self.data.videoPlayer.processor.process = self.processFrame
        layout.addWidget(self.data)
        layout.addSpacing(PAD_Y)
        self.data.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        # Experiment settings
        self.settings = Monocular2DSettingsPanel(self)
        self.settings.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )
        self.settings.exportButton.clicked.connect(self.downloadMotionData)
        layout.addWidget(self.settings)

        # Connect the update event
        self.data.onUpdate = self.handleDataUpload
        self.settings.onUpdate = self.handleOptionsChanged

        # Model setup
        self.model = None

        # TODO: Data streaming
        self.streamer = None
        if FEATURE_STREAMING_ENABLED:
            self.streamer = MotionDataStreamer(host="0.0.0.0", port=8765)

    def setExperiment(self, name):
        self.experiment = Experiment.open(name)
        self.data.setExperiment(self.experiment)
        self.settings.setExperiment(self.experiment)
        self.refreshUI()

        if self.streamer is not None:
            self.streamer.stop()
            server_thread = threading.Thread(target=self.streamer.start)
            server_thread.start()

    def refreshUI(self):
        if self.experiment is None:
            return

        # Model setup
        # TODO: Refresh model when experiment settings are updated
        self.model = setup_pose_tracker(self.experiment.cfg)

        self.all_frames_X = []
        self.all_frames_Y = []
        self.all_frames_scores = []
        self.all_frames_angles = []
        self.postprocessing_kwargs = {}
        # frame_count, frame_rate, fps, save_pose, pose_output_path, save_angles, angles_output_path

    def processFrame(self, frame):
        if self.model is None:
            return frame

        frame, motion_data = process_frame(self.experiment.cfg, self.model, frame)

        if self.streamer is not None:
            async def send_motion_data(motion_data):
                xs, ys, scores, angles, metainfo = motion_data
                image_size = frame.shape[:2]
                data = {
                    "keypoints": [
                        {"x": x, "y": y, "score": s} for x, y, s in zip(xs, ys, scores)
                    ],
                    "angles": angles,
                    "metadata": {
                        "image_size": image_size,
                        "timestamp": time.time(),
                        **metainfo,
                    },
                }
                await self.streamer.stream_frame(data)

            asyncio.run(send_motion_data(motion_data))

        return frame

    def handleDataUpload(self, status):
        self.settings.setEnabled(status)

    def handleOptionsChanged(self, status, result):
        if not status:
            self.showAlert(str(result), "Motion Estimation Failed")

    def downloadMotionData(self):
        try:
            motionData = self.experiment.get_motion_file()
            self.downloadFile(motionData)
        except Exception as e:
            self.showAlert(str(e), "Download Failed")

    def downloadFile(self, file_path):
        # Show a download dialog
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.selectFile(os.path.basename(file_path))

        if file_dialog.exec():
            save_path = file_dialog.selectedFiles()[0]
            if save_path:
                shutil.copyfile(file_path, save_path)
                # TOOD: Show a success message

    def __atexit__(self):
        if self.streamer is not None:
            logging.debug("Stopping the WebSocket server.")  # FIXME: Hack
            self.streamer.stop()
