from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
)

from TracX.ui.common import LabeledWidget, MultipleSelection, Selection
from TracX.ui.styles import PAD_Y

from ..base.settings import SettingsPanel


class Monocular2DSettingsPanel(SettingsPanel):
    def __init__(self, parent):
        super().__init__("Monocular 2D Analysis", parent)

    def initPoseOptions(self, scroll_layout):
        # section subheading
        heading = QLabel("Pose Estimation", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)

        # [pose] pose_model
        self.pose_model = Selection(
            "Pose Model",
            {
                "UE5": "BODY_53",
                "Body": "COCO_17",
                "Body + Feet": "HALPE_26",
                "Body + Feet + Spine": "BODY_43",
                "Full Body": "COCO_133",
                "Full Body + Spine": "WHOLEBODY_150",
                "Hands": "HAND_21",
                "Face": "FACE_106",
            },
            self,
        )
        self.pose_model.setToolTip("Pose model to use.")
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

    def initAnglesOptions(self, main_layout):
        # section subheading
        heading = QLabel("Kinematic Angles", self)
        heading.setProperty("class", "h2")
        main_layout.addWidget(heading)
        main_layout.addSpacing(PAD_Y // 2)

        # [angles] joint_angles
        self.joint_angles = MultipleSelection(
            "Joint Angles",
            {
                "Right Ankle": "Right ankle",
                "Left Ankle": "Left ankle",
                "Right Knee": "Right knee",
                "Left Knee": "Left knee",
                "Right Hip": "Right hip",
                "Left Hip": "Left hip",
                "Right Shoulder": "Right shoulder",
                "Left Shoulder": "Left shoulder",
                "Right Elbow": "Right elbow",
                "Left Elbow": "Left elbow",
                "Right Wrist": "Right wrist",
                "Left Wrist": "Left wrist",
            },
            self,
        )
        self.joint_angles.setToolTip(
            "Select joint angles to compute from the available options."
        )
        main_layout.addWidget(self.joint_angles)

        # [angles] segment_angles
        self.segment_angles = MultipleSelection(
            "Segment Angles",
            {
                "Right Foot": "Right foot",
                "Left Foot": "Left foot",
                "Right Shank": "Right shank",
                "Left Shank": "Left shank",
                "Right Thigh": "Right thigh",
                "Left Thigh": "Left thigh",
                "Pelvis": "Pelvis",
                "Trunk": "Trunk",
                "Shoulders": "Shoulders",
                "Head": "Head",
                "Right Arm": "Right arm",
                "Left Arm": "Left arm",
                "Right Forearm": "Right forearm",
                "Left Forearm": "Left forearm",
            },
            self,
        )
        self.segment_angles.setToolTip(
            "Select segment angles to compute from the available options."
        )
        main_layout.addWidget(self.segment_angles)

        # [angles] flip_left_right
        self.flip_left_right = LabeledWidget(
            "Flip Left/Right",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.flip_left_right.widget.setFixedWidth(24)
        self.flip_left_right.widget.setToolTip(
            "Enable this to compute the same angles whether the participant faces left or right."
        )
        main_layout.addWidget(self.flip_left_right)

        # [angles] display_angle_values_on
        self.display_angle_values_on = Selection(
            "Display Angle Values On",
            {
                "None": None,
                "Body": "body",
                "List": "list",
                "Both": "['body', 'list']",
            },
            self,
        )
        self.display_angle_values_on.setToolTip(
            "Choose where to display angle values: 'body', 'list', both, or none."
        )
        main_layout.addWidget(self.display_angle_values_on)

        # [angles] fontSize
        self.font_size = LabeledWidget(
            "Font Size",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.font_size.widget.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 1))
        self.font_size.widget.setFixedWidth(48)
        self.font_size.widget.setToolTip(
            "Set the font size for displayed angle values."
        )
        main_layout.addWidget(self.font_size)

    def initPostProcessingOptions(self, scroll_layout):
        # section subheading
        heading = QLabel("Post-Processing", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)
        scroll_layout.addSpacing(PAD_Y // 2)

        heading = QLabel("Interpolation", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [post-processing] interpolate
        self.interpolate = LabeledWidget(
            "Interpolate Missing Data",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.interpolate.widget.setFixedWidth(24)
        self.interpolate.widget.setToolTip(
            "Enable interpolation for small gaps in data."
        )
        scroll_layout.addWidget(self.interpolate)

        # [post-processing] interp_gap_smaller_than
        self.interp_gap_smaller_than = LabeledWidget(
            "Interpolate Gaps Smaller Than",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.interp_gap_smaller_than.widget.setValidator(QtGui.QIntValidator(1, 100))
        self.interp_gap_smaller_than.widget.setFixedWidth(48)
        self.interp_gap_smaller_than.widget.setToolTip(
            "Specify the maximum gap size (in frames) for interpolation."
        )
        scroll_layout.addWidget(self.interp_gap_smaller_than)

        # [post-processing] fill_large_gaps_with
        self.fill_large_gaps_with = Selection(
            "Fill Large Gaps With",
            {
                "Last Value": "last_value",
                "NaN": "nan",
                "Zeros": "zeros",
            },
            self,
        )
        self.fill_large_gaps_with.setToolTip(
            "Choose the method for filling large gaps in data: 'last_value', 'nan', or 'zeros'."
        )
        scroll_layout.addWidget(self.fill_large_gaps_with)

        heading = QLabel("Filtering", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [post-processing] filter
        self.filter = LabeledWidget(
            "Apply Filter",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.filter.widget.setFixedWidth(24)
        self.filter.widget.setToolTip("Enable filtering for smoothing the results.")
        scroll_layout.addWidget(self.filter)

        # [post-processing] filter_type
        self.filter_type = Selection(
            "Filter Type",
            {
                "Butterworth": "butterworth",
                "Gaussian": "gaussian",
                "LOESS": "loess",
                "Median": "median",
            },
            self,
        )
        self.filter_type.setToolTip(
            "Select the filter type: Butterworth, Gaussian, LOESS, or Median."
        )
        scroll_layout.addWidget(self.filter_type)

        # [post-processing.butterworth] order and cut_off_frequency
        self.butterworth_order = LabeledWidget(
            "Order",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.butterworth_order.widget.setValidator(QtGui.QIntValidator(1, 10))
        self.butterworth_order.widget.setFixedWidth(48)
        self.butterworth_order.widget.setToolTip(
            "Set the order of the Butterworth filter."
        )
        scroll_layout.addWidget(self.butterworth_order)

        self.butterworth_cut_off_frequency = LabeledWidget(
            "Cut-Off Frequency",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.butterworth_cut_off_frequency.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 1)
        )
        self.butterworth_cut_off_frequency.widget.setFixedWidth(48)
        self.butterworth_cut_off_frequency.widget.setToolTip(
            "Set the cut-off frequency (Hz) for the Butterworth filter."
        )
        scroll_layout.addWidget(self.butterworth_cut_off_frequency)

    def initVisualizationOptions(self, main_layout):
        heading = QLabel("Visualizations", self)
        heading.setProperty("class", "h2")
        main_layout.addWidget(heading)

        # [post-processing] show_graphs
        self.show_graphs = LabeledWidget(
            "Show Graphs",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.show_graphs.widget.setFixedWidth(24)
        self.show_graphs.widget.setToolTip(
            "Enable this to display plots of raw and processed data."
        )
        main_layout.addWidget(self.show_graphs)

    def initScrollAreaContent(self, scroll_layout):
        # Pose settings
        self.initPoseOptions(scroll_layout)

        # Angles settings
        scroll_layout.addSpacing(PAD_Y // 2)
        self.initAnglesOptions(scroll_layout)

        # Post-processing settings
        scroll_layout.addSpacing(PAD_Y // 2)
        self.initPostProcessingOptions(scroll_layout)

        # Visualizations
        scroll_layout.addSpacing(PAD_Y // 2)
        self.initVisualizationOptions(scroll_layout)

    def refreshUI(self):
        super().refreshUI()
        if self.experiment is None:
            return

        # Get the experiment config
        cfg = self.experiment.cfg

        # Show experiment pose settings
        self.multiperson.widget.setChecked(cfg["process"]["multiperson"])
        self.tracking_mode.setOption(cfg["pose"]["tracking_mode"])
        self.keypoint_likelihood_threshold.widget.setText(
            str(cfg["pose"]["keypoint_likelihood_threshold"])
        )
        self.average_likelihood_threshold.widget.setText(
            str(cfg["pose"]["average_likelihood_threshold"])
        )
        self.keypoint_number_threshold.widget.setText(
            str(cfg["pose"]["keypoint_number_threshold"])
        )

        # Show experiment angles settings
        display_angle_values_on = cfg["angles"].get("display_angle_values_on", "Both")
        if isinstance(display_angle_values_on, list):
            display_angle_values_on = "Both"
        self.display_angle_values_on.widget.setCurrentText(display_angle_values_on)
        self.font_size.widget.setText(str(cfg["angles"]["fontSize"]))
        self.joint_angles.setOption(", ".join(cfg["angles"]["joint_angles"]))
        self.segment_angles.setOption(", ".join(cfg["angles"]["segment_angles"]))
        self.flip_left_right.widget.setChecked(cfg["angles"]["flip_left_right"])

        # Show experiment post-processing settings
        self.interpolate.widget.setChecked(cfg["post-processing"]["interpolate"])
        self.interp_gap_smaller_than.widget.setText(
            str(cfg["post-processing"]["interp_gap_smaller_than"])
        )
        self.fill_large_gaps_with.setOption(
            cfg["post-processing"]["fill_large_gaps_with"]
        )
        self.filter.widget.setChecked(cfg["post-processing"]["filter"])
        self.show_graphs.widget.setChecked(cfg["post-processing"]["show_graphs"])
        self.filter_type.setOption(cfg["post-processing"]["filter_type"])
        self.butterworth_order.widget.setText(
            str(cfg["post-processing"]["butterworth"]["order"])
        )
        self.butterworth_cut_off_frequency.widget.setText(
            str(cfg["post-processing"]["butterworth"]["cut_off_frequency"])
        )

        # Update buttons
        self.analyzeButton.log_file = self.experiment.log_file

    def updateConfig(self, cfg):
        cfg = super().updateConfig(cfg)

        ## Pose > Detection
        cfg["pose"]["keypoint_likelihood_threshold"] = float(
            self.keypoint_likelihood_threshold.widget.text()
        )
        cfg["pose"]["average_likelihood_threshold"] = float(
            self.average_likelihood_threshold.widget.text()
        )
        cfg["pose"]["keypoint_number_threshold"] = float(
            self.keypoint_number_threshold.widget.text()
        )

        ## Pose > Tracking
        cfg["process"]["multiperson"] = self.multiperson.widget.isChecked()
        cfg["pose"]["tracking_mode"] = self.tracking_mode.selected_option

        # Angles settings
        cfg["angles"]["joint_angles"] = self.joint_angles.selected_options
        cfg["angles"]["segment_angles"] = self.segment_angles.selected_options
        cfg["angles"]["flip_left_right"] = self.flip_left_right.widget.isChecked()
        cfg["angles"]["display_angle_values_on"] = (
            self.display_angle_values_on.selected_option
        )
        cfg["angles"]["fontSize"] = float(self.font_size.widget.text())

        # Post-processing settings
        ## Post-processing > Interpolation
        cfg["post-processing"]["interpolate"] = self.interpolate.widget.isChecked()
        cfg["post-processing"]["interp_gap_smaller_than"] = int(
            self.interp_gap_smaller_than.widget.text()
        )
        cfg["post-processing"]["fill_large_gaps_with"] = (
            self.fill_large_gaps_with.selected_option
        )

        ## Post-processing > Filtering
        cfg["post-processing"]["filter"] = self.filter.widget.isChecked()
        cfg["post-processing"]["filter_type"] = self.filter_type.selected_option
        cfg["post-processing"]["butterworth"]["order"] = int(
            self.butterworth_order.widget.text()
        )
        cfg["post-processing"]["butterworth"]["cut_off_frequency"] = float(
            self.butterworth_cut_off_frequency.widget.text()
        )

        # Visualization settings
        cfg["post-processing"]["show_graphs"] = self.show_graphs.widget.isChecked()

        return cfg
