from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from mocap.ui.common import IconButton, LabeledWidget, Selection
from mocap.ui.styles import PAD_Y

from ..buttons import EstimateMotionButton, OpenSimButton, VisualizeMotionButton
from ..monocular2d.settings import SettingsPanel


class Multiview3DSettingsPanel(SettingsPanel):
    def __init__(self, parent):
        super().__init__("Multiview 3D Analysis", parent)

    def initScrollAreaContent(self, scroll_layout):
        # section subheading
        heading = QLabel("Pose Estimation", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)

        # self.correctRotationCheckbox = QCheckBox("Fix Rotation", self)
        # self.correctRotationCheckbox.setProperty("class", "body")
        # scroll_layout.addWidget(self.correctRotationCheckbox)

        # [project] multi_person
        self.multiperson = LabeledWidget(
            "Multiple People",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.multiperson.widget.setFixedWidth(24)
        self.multiperson.setToolTip("Enable multi-person pose estimation.")
        self.multiperson.setEnabled(False)
        scroll_layout.addWidget(self.multiperson)

        # [project] participant_height
        self.participant_height = LabeledWidget(
            "Participant Height (m)",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.participant_height.setToolTip(
            "Participant height in meters. Only used for marker augmentation."
        )
        self.participant_height.widget.setFixedWidth(48)
        self.participant_height.widget.setValidator(QtGui.QDoubleValidator(1.0, 2.0, 2))
        scroll_layout.addWidget(self.participant_height)

        # [project] participant_mass
        self.participant_mass = LabeledWidget(
            "Participant Mass (kg)",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.participant_mass.setToolTip(
            "Participant mass in kilograms. Only used for marker augmentation and scaling."
        )
        self.participant_mass.widget.setFixedWidth(48)
        self.participant_mass.widget.setValidator(
            QtGui.QDoubleValidator(10.0, 200.0, 2)
        )

        # [pose] pose_model
        self.pose_model = Selection(
            "Skeleton",
            {
                "Body": "COCO_17",
                "Body + Feet": "HALPE_26",
                "Body + Feet + Spine": "DFKI_BODY43",
                "Spine Only": "DFKI_SPINE17",
                "Full Body": "COCO_133",
            },
            self,
        )
        self.pose_model.changed.connect(self.onSkeletonChanged)
        scroll_layout.addWidget(self.pose_model)
        scroll_layout.addSpacing(8)

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

        # [pose] tracking
        self.tracking = LabeledWidget(
            "Tracking",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.tracking.setToolTip(
            "Enable tracking of detected people to get a consistent person ID across frames. Slightly slower but might facilitate synchronization if other people are in the background."
        )
        self.tracking.widget.setFixedWidth(24)
        scroll_layout.addWidget(self.tracking)

        # [pose] overwrite_pose
        self.overwrite_pose = LabeledWidget(
            "Overwrite Pose",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.overwrite_pose.setToolTip(
            "Set to false if you don't want to recalculate pose estimation when it has already been done"
        )
        self.overwrite_pose.widget.setFixedWidth(24)
        scroll_layout.addWidget(self.overwrite_pose)

        # [pose] save_video
        self.save_video = LabeledWidget(
            "Save Visualizations",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.save_video.setToolTip("Save 2D pose visualizations to disk.")
        self.save_video.widget.setFixedWidth(24)
        scroll_layout.addWidget(self.save_video)

        # section subheading
        heading = QLabel("Post-Processing", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)
        scroll_layout.addSpacing(PAD_Y // 2)

        heading = QLabel("Person Association", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [personAssociation] likelihood_threshold_association
        self.likelihood_threshold_association = LabeledWidget(
            "Likelihood",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.likelihood_threshold_association.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 1.0, 1)
        )
        self.likelihood_threshold_association.widget.setFixedWidth(48)
        self.likelihood_threshold_association.widget.setToolTip(
            "Threshold for person association. Persons above this threshold are considered the same person. Lower values are more strict."
        )
        scroll_layout.addWidget(self.likelihood_threshold_association)

        # [personAssociation]reproj_error_threshold_association
        self.reproj_error_threshold_association = LabeledWidget(
            "Reprojection Error (px)",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.reproj_error_threshold_association.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 1)
        )
        self.reproj_error_threshold_association.widget.setFixedWidth(48)
        self.reproj_error_threshold_association.widget.setToolTip(
            "Reprojection error threshold for person association. Persons with a higher error are considered different. Lower values are more strict."
        )
        scroll_layout.addWidget(self.reproj_error_threshold_association)

        # [personAssociation] tracked_keypoint
        # FIXME: Should be a dropdown with names of keypoints available in the current model
        self.tracked_keypoint = LabeledWidget(
            "Tracked Keypoint",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.tracked_keypoint.widget.setFixedWidth(48)
        self.tracked_keypoint.widget.setToolTip(
            "Keypoint to track for person association. Choose a stable point for tracking the person of interest"
        )

        heading = QLabel("Triangulation", self)
        heading.setProperty("class", "h3")
        heading.setWordWrap(True)
        scroll_layout.addWidget(heading)

        # [triangulation] likelihood_threshold_triangulation
        self.likelihood_threshold_triangulation = LabeledWidget(
            "Likelihood",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.likelihood_threshold_triangulation.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 1.0, 1)
        )
        self.likelihood_threshold_triangulation.widget.setFixedWidth(48)
        self.likelihood_threshold_triangulation.widget.setToolTip(
            "Threshold for triangulation. Points above this threshold are considered valid. Lower values are more strict."
        )
        scroll_layout.addWidget(self.likelihood_threshold_triangulation)

        # [triangulation] reproj_error_threshold (px)
        self.reproj_error_threshold = LabeledWidget(
            "Reprojection Error (px)",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.reproj_error_threshold.widget.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 1)
        )
        self.reproj_error_threshold.widget.setFixedWidth(48)
        self.reproj_error_threshold.widget.setToolTip(
            "Reprojection error threshold for triangulation. Lower values are more strict."
        )

        # [triangulation] min_cameras_for_triangulation
        self.min_cameras_for_triangulation = LabeledWidget(
            "Min Cameras",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.min_cameras_for_triangulation.widget.setValidator(
            QtGui.QIntValidator(2, 10)
        )
        self.min_cameras_for_triangulation.widget.setFixedWidth(48)
        self.min_cameras_for_triangulation.widget.setToolTip(
            "Minimum number of cameras required to triangulate a point. An error is raised if fewer cameras have a valid point."
        )
        scroll_layout.addWidget(self.min_cameras_for_triangulation)

        heading = QLabel("Interpolation", self)
        heading.setProperty("class", "h3")
        heading.setWordWrap(True)
        scroll_layout.addWidget(heading)

        # [triangulation] interpolation
        self.interpolation = Selection(
            "Interpolation Method",
            {
                "Linear": "linear",
                "Cubic": "cubic",
                "Spline": "slinear",
                "Quadratic": "quadratic",
                "None": "none",
            },
            self,
        )
        self.interpolation.setToolTip(
            "Interpolation method for missing frames. 'None' will not interpolate, 'linear' will interpolate linearly, 'cubic' will interpolate with a cubic spline, 'slinear' will interpolate with a spline of degree 1, and 'quadratic' will interpolate with a spline of degree 2."
        )
        scroll_layout.addWidget(self.interpolation)

        # [triangulation] interpolation_frequency
        self.interp_if_gap_smaller_than = LabeledWidget(
            "Interpolate Gaps Smaller Than",
            QLineEdit(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.interp_if_gap_smaller_than.widget.setValidator(QtGui.QIntValidator(1, 100))
        self.interp_if_gap_smaller_than.widget.setFixedWidth(48)
        self.interp_if_gap_smaller_than.widget.setToolTip(
            "Specify the maximum gap size (in frames) for interpolation."
        )
        scroll_layout.addWidget(self.interp_if_gap_smaller_than)

        # [triangulation] fill_large_gaps_with
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

        # [triangulation] undistort_points
        self.undistort_points = LabeledWidget(
            "Undistort Points",
            QCheckBox(self),
            style="body",
            orientation=Qt.Orientation.Horizontal,
        )
        self.undistort_points.widget.setFixedWidth(24)
        self.undistort_points.setToolTip(
            "Undistort points before triangulation. Better if distorted image (parallel lines curvy on the edge or at least one param > 10^-2), but unnecessary (and slightly slower) if distortions are low."
        )
        scroll_layout.addWidget(self.undistort_points)

        # filtering
        heading = QLabel("Filtering", self)
        heading.setProperty("class", "h3")
        scroll_layout.addWidget(heading)

        # [filtering] filter_type
        self.filter_type = Selection(
            "Filter Type",
            {
                "Butterworth": "butterworth",
                "Kalman": "kalman",
                "Gaussian": "gaussian",
                "LOESS": "loess",
                "Median": "median",
                "Butterworth On Speed": "butterworth_on_speed",
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

        # Scaling Settings
        heading = QLabel("Simulation Setup", self)
        heading.setProperty("class", "h2")
        scroll_layout.addWidget(heading)

        # [simulation] simulation_type (matplotlib, opensim, blender, unrealengine)
        self.simulation_type = Selection(
            "Simulation Type",
            {
                "Stick Figure": "matplotlib",
                "OpenSim": "opensim",
                "Blender": "blender",
                "Unreal Engine": "unrealengine",
            },
            self,
        )
        self.simulation_type.setToolTip(
            "Select the simulation type: Stick Figure, OpenSim, Blender, or Unreal Engine."
        )
        scroll_layout.addWidget(self.simulation_type)

    def initButtonBar(self, main_layout):
        # Button bar
        button_bar = QWidget(self)
        button_bar.setProperty("class", "empty")
        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        main_layout.addWidget(button_bar)

        # Save Button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.applyConfigChanges)
        layout.addWidget(self.saveButton)

        # Create Button
        self.estimateButton = EstimateMotionButton(self.onMotionEstimated)
        layout.addWidget(self.estimateButton)

        self.downloadButton = IconButton("export.png", 24, self)
        layout.addWidget(self.downloadButton)

        # Create Button
        self.createButton = VisualizeMotionButton(self.onVisualized)
        layout.addWidget(self.createButton)

        self.downloadOpenSimButton = OpenSimButton(self.onExportReady)
        layout.addWidget(self.downloadOpenSimButton)

        self.onUpdate = lambda status, result: None

    def refreshUI(self):
        super().refreshUI()
        if self.experiment is None:
            return

        # Get the experiment config
        cfg = self.experiment.cfg

        # Update the UI elements
        self.multiperson.widget.setChecked(cfg["project"]["multi_person"])
        self.participant_height.widget.setText(
            str(cfg["project"]["participant_height"])
        )
        self.participant_mass.widget.setText(str(cfg["project"]["participant_mass"]))
        self.tracking.widget.setChecked(cfg["pose"]["tracking"])
        self.overwrite_pose.widget.setChecked(cfg["pose"]["overwrite_pose"])
        self.save_video.widget.setChecked(cfg["pose"]["save_video"] == "to_video")

        self.likelihood_threshold_association.widget.setText(
            str(cfg["personAssociation"]["likelihood_threshold_association"])
        )
        self.reproj_error_threshold_association.widget.setText(
            str(
                cfg["personAssociation"]["single_person"][
                    "reproj_error_threshold_association"
                ]
            )
        )
        self.tracked_keypoint.widget.setText(
            cfg["personAssociation"]["single_person"]["tracked_keypoint"]
        )

        self.likelihood_threshold_triangulation.widget.setText(
            str(cfg["triangulation"]["likelihood_threshold_triangulation"])
        )
        self.reproj_error_threshold.widget.setText(
            str(cfg["triangulation"]["reproj_error_threshold_triangulation"])
        )
        self.min_cameras_for_triangulation.widget.setText(
            str(cfg["triangulation"]["min_cameras_for_triangulation"])
        )

        self.interpolation.setOption(cfg["triangulation"]["interpolation"])
        self.interp_if_gap_smaller_than.widget.setText(
            str(cfg["triangulation"]["interp_if_gap_smaller_than"])
        )
        self.fill_large_gaps_with.setOption(
            cfg["triangulation"]["fill_large_gaps_with"]
        )
        self.undistort_points.widget.setChecked(
            cfg["triangulation"]["undistort_points"]
        )

        self.filter_type.setOption(cfg["filtering"]["type"])
        self.butterworth_order.widget.setText(
            str(cfg["filtering"]["butterworth"]["order"])
        )
        self.butterworth_cut_off_frequency.widget.setText(
            str(cfg["filtering"]["butterworth"]["cut_off_frequency"])
        )

        # Update buttons
        self.estimateButton.task.config = self.experiment.name
        self.createButton.task.config = self.experiment.name
        self.downloadOpenSimButton.task.config = self.experiment.name

    def updateConfig(self, cfg):
        cfg = super().updateConfig(cfg)

        cfg["project"]["multi_person"] = self.multiperson.widget.isChecked()
        cfg["project"]["participant_height"] = float(
            self.participant_height.widget.text()
        )
        cfg["project"]["participant_mass"] = float(self.participant_mass.widget.text())
        cfg["pose"]["tracking"] = self.tracking.widget.isChecked()
        cfg["pose"]["overwrite_pose"] = self.overwrite_pose.widget.isChecked()
        cfg["pose"]["save_video"] = (
            "to_video" if self.save_video.widget.isChecked() else "none"
        )

        cfg["personAssociation"]["likelihood_threshold_association"] = float(
            self.likelihood_threshold_association.widget.text()
        )
        cfg["personAssociation"]["single_person"][
            "reproj_error_threshold_association"
        ] = float(self.reproj_error_threshold_association.widget.text())
        cfg["personAssociation"]["single_person"]["tracked_keypoint"] = (
            self.tracked_keypoint.widget.text()
        )

        cfg["triangulation"]["likelihood_threshold_triangulation"] = float(
            self.likelihood_threshold_triangulation.widget.text()
        )
        cfg["triangulation"]["reproj_error_threshold_triangulation"] = float(
            self.reproj_error_threshold.widget.text()
        )
        cfg["triangulation"]["min_cameras_for_triangulation"] = int(
            self.min_cameras_for_triangulation.widget.text()
        )

        cfg["triangulation"]["interpolation"] = self.interpolation.selected_option
        cfg["triangulation"]["interp_if_gap_smaller_than"] = int(
            self.interp_if_gap_smaller_than.widget.text()
        )
        cfg["triangulation"]["fill_large_gaps_with"] = (
            self.fill_large_gaps_with.selected_option
        )
        cfg["triangulation"]["undistort_points"] = (
            self.undistort_points.widget.isChecked()
        )

        cfg["filtering"]["type"] = self.filter_type.selected_option
        cfg["filtering"]["butterworth"]["order"] = int(
            self.butterworth_order.widget.text()
        )
        cfg["filtering"]["butterworth"]["cut_off_frequency"] = float(
            self.butterworth_cut_off_frequency.widget.text()
        )

        return cfg

    def toggleCorrectRotation(self):
        self.params.correct_rotation = self.correctRotationCheckbox.isChecked()

    def onSkeletonChanged(self, skeleton):
        # TODO: Update available modes based on the selected skeleton
        pass

    def onMotionEstimated(self, status, result):
        self.onUpdate(status, result)
        self.downloadButton.setEnabled(status)

    def onVisualized(self, status, result):
        pass

    def onExportReady(self, status, result):
        pass
