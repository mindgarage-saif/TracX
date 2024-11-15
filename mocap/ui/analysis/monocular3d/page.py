import os
import shutil

import cv2
from PyQt6.QtWidgets import (
    QFileDialog,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mocap.core import Experiment
from mocap.core.analyze2d import process_frame, setup_pose_tracker
from mocap.ui.styles import PAD_Y

from .data_widget import ExperimentDataWidget
from .motion_options import MotionOptions


class MonocularAnalysisPage(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Experiment data
        self.data = ExperimentDataWidget(self)
        self.data.videoPlayer.videoProcessor.process = self.processFrame
        layout.addWidget(self.data)
        layout.addSpacing(PAD_Y)
        self.data.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )

        # Experiment settings
        self.settings = MotionOptions(self)
        self.settings.downloadButton.clicked.connect(self.downloadMotionData)
        layout.addWidget(self.settings)

        # Connect the update event
        self.data.onUpdate = self.handleDataUpload
        self.settings.onUpdate = self.handleOptionsChanged

        # mode = self.experiment.cfg.get("pose").get("mode")
        # tracking = self.experiment.cfg.get("process").get("multiperson")
        # det_frequency = self.experiment.cfg.get("pose").get("det_frequency")
        # tracking_mode = self.experiment.cfg.get("pose").get("tracking_mode")
        # tracking_rtmlib = tracking_mode == "rtmlib" and tracking
        # self.model = setup_pose_tracker(det_frequency, mode, tracking_rtmlib)

        self.model = setup_pose_tracker(10, "lightweight", False)

        # self.model = PoseTracker(
        #     BodyWithFeet,
        #     det_frequency=30,
        #     tracking=False,
        #     mode="balanced",
        #     to_openpose=False,
        #     backend="onnxruntime",
        #     device="cuda",
        # )

    def load(self, name):
        self.settings.cfg.experiment_name = name
        self.settings.visualize_cfg.experiment_name = name  # FIXME: This is a hack
        self.experiment = Experiment.open(name)
        self.data.setExperiment(self.experiment)
        hasMotionData = self.experiment.get_motion_file() is not None
        self.settings.estimate_button.setEnabled(
            not hasMotionData,
        )
        self.settings.downloadButton.setEnabled(hasMotionData)

        self.settings.estimate_button.log_file = self.experiment.log_file

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

        return process_frame(self.experiment.cfg, self.model, frame)

        # frame = cv2.flip(frame, 1)
        # self.drawRecordingOverlay(frame)
        # frame = cv2.flip(frame, 1)
        # return frame

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
