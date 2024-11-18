import os
import shutil

import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)

from mocap.core import Experiment
from mocap.core.analyze2d import process_frame, setup_pose_tracker
from mocap.ui.styles import PAD_Y

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
        self.data.videoPlayer.videoProcessor.process = self.processFrame
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

    def setExperiment(self, name):
        self.experiment = Experiment.open(name)
        self.data.setExperiment(self.experiment)
        self.settings.setExperiment(self.experiment)
        self.refreshUI()

    def refreshUI(self):
        if self.experiment is None:
            return

        # Model setup
        # TODO: Refresh model when experiment settings are updated
        mode = self.experiment.cfg.get("pose").get("mode")
        det_frequency = self.experiment.cfg.get("pose").get("det_frequency")
        tracking_mode = self.experiment.cfg.get("pose").get("tracking_mode")
        tracking = self.experiment.cfg.get("process").get("multiperson")
        tracking_rtmlib = tracking_mode == "rtmlib" and tracking
        self.model = setup_pose_tracker(det_frequency, mode, tracking_rtmlib)

        self.all_frames_X = []
        self.all_frames_Y = []
        self.all_frames_scores = []
        self.all_frames_angles = []
        self.postprocessing_kwargs = {}
        # frame_count, frame_rate, fps, save_pose, pose_output_path, save_angles, angles_output_path

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

    def processFrame(self, frame):
        # TODO: Perform post-processing
        # keypoints, scores = self.model(frame)
        # frame = draw_skeleton(frame, keypoints, scores, openpose_skeleton=False, kpt_thr=0.43)

        if self.model is None:
            return frame

        frame, (x, y, scores, angles, kwargs) = process_frame(
            self.experiment.cfg, self.model, frame
        )
        self.all_frames_X.append(np.array(x))
        self.all_frames_Y.append(np.array(y))
        self.all_frames_scores.append(np.array(scores))
        self.all_frames_angles.append(np.array(angles))
        self.postprocessing_kwargs = kwargs

        print(kwargs["keypoint_names"])
        print(x, y)
        print(kwargs["angle_names"])
        print(angles)

        # frame = cv2.flip(frame, 1)
        # self.drawRecordingOverlay(frame)
        # frame = cv2.flip(frame, 1)
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
