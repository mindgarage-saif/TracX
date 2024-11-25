from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
)

from TracX.ui.common import LabeledWidget, Selection

from ..monocular2d.settings import SettingsPanel


class Monocular3DSettingsPanel(SettingsPanel):
    def __init__(self, parent):
        super().__init__("Monocular 3D Analysis", parent)

    def initScrollAreaContent(self, scroll_layout):
        # section subheading
        heading = QLabel("Pose Estimation", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)

        # [pose] pose_model
        self.pose_model = Selection(
            "Pose Model",
            {"Body + Feet": "body_with_feet"},
            self,
        )
        self.pose_model.setToolTip(
            "Pose model to use. Currently, only 'body_with_feet' is supported."
        )
        scroll_layout.addWidget(self.pose_model)

        # [pose] mode
        self.perfomance_mode = Selection(
            "Performance Mode",
            {
                "Lite": "lightweight",
                "Medium": "balanced",
                "Heavy": "performance",
            },
            self,
        )
        self.perfomance_mode.setToolTip(
            "Performance mode: 'lightweight' for speed, 'balanced' for a mix, and 'performance' for accuracy."
        )
        scroll_layout.addWidget(self.perfomance_mode)

        heading = QLabel("Detection", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [pose] det_frequency
        self.det_frequency = LabeledWidget(
            "Detection Frequency",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.det_frequency.widget.setValidator(QtGui.QIntValidator(1, 100))
        self.det_frequency.widget.setFixedWidth(48)
        self.det_frequency.widget.setToolTip(
            "Run person detection only every N frames. Tracking is used for intermediate frames."
        )
        scroll_layout.addWidget(self.det_frequency)

        # [pose] keypoint_likelihood_threshold
        self.keypoint_likelihood_threshold = LabeledWidget(
            "Keypoint Likelihood Threshold",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.keypoint_likelihood_threshold.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 1.0, 1)
        )
        self.keypoint_likelihood_threshold.widget.setFixedWidth(48)
        self.keypoint_likelihood_threshold.widget.setToolTip(
            "Keypoints with likelihood below this value will be ignored."
        )
        scroll_layout.addWidget(self.keypoint_likelihood_threshold)

        # [pose] keypoint_number_threshold
        self.keypoint_number_threshold = LabeledWidget(
            "Keypoint Number Threshold",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.keypoint_number_threshold.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 1.0, 1)
        )
        self.keypoint_number_threshold.widget.setFixedWidth(48)
        self.keypoint_number_threshold.widget.setToolTip(
            "Persons with fewer good keypoints than this fraction will be ignored."
        )
        scroll_layout.addWidget(self.keypoint_number_threshold)

        # [pose] average_likelihood_threshold
        self.average_likelihood_threshold = LabeledWidget(
            "Person Likelihood Threshold",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.average_likelihood_threshold.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 1.0, 1)
        )
        self.average_likelihood_threshold.widget.setFixedWidth(48)
        self.average_likelihood_threshold.widget.setToolTip(
            "Persons with an average keypoint likelihood below this value will be ignored."
        )
        scroll_layout.addWidget(self.average_likelihood_threshold)

        heading = QLabel("Tracking", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [process] multiperson
        self.multiperson = LabeledWidget(
            "Multiperson",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.multiperson.widget.setFixedWidth(24)
        self.multiperson.widget.setToolTip(
            "Multiperson involves tracking: will be faster if false"
        )
        scroll_layout.addWidget(self.multiperson)

        # [pose] tracking_mode
        self.tracking_mode = Selection(
            "Tracking Mode",
            {
                "Sports2D": "sports2d",
                "RTMLib": "rtmlib",
            },
            self,
        )
        self.tracking_mode.setToolTip(
            "Tracking mode: 'sports2d' is more accurate, 'rtmlib' may be faster."
        )
        scroll_layout.addWidget(self.tracking_mode)
