import contextlib
import os

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from TracX.core import Experiment
from TracX.core.cameras import CameraSystem, CameraVisualizer
from TracX.ui.common import LabeledWidget, MatrixWidget, Tab, TabbedArea
from TracX.ui.styles import PAD_Y


class CamerasTab(Tab):
    def __init__(self, parent):
        super().__init__("Cameras", parent, Qt.Orientation.Horizontal)
        self.cameras = None
        self.visualizer = None
        self.canvas = None
        self.experiment = None

        # Panel 1: Adding cameras and defining/importing calibration parameters
        camerasLayout = QVBoxLayout()
        camerasLayout.setContentsMargins(0, 0, 0, 0)
        camerasLayout.setSpacing(PAD_Y)
        self.addLayout(camerasLayout)

        # Panel 2: Visualization of camera calibration
        self.canvasLayout = QVBoxLayout()
        self.canvasLayout.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout.setSpacing(0)
        self.addLayout(self.canvasLayout)

        # Divide panel 1 into two vertical sections, one for adding
        # cameras and the other for modifying calibration parameters
        camerasLayout1 = QVBoxLayout()
        camerasLayout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        camerasLayout1.setContentsMargins(0, 0, 0, 0)
        camerasLayout1.setSpacing(0)

        camerasLayout2 = QVBoxLayout()
        camerasLayout2.setAlignment(Qt.AlignmentFlag.AlignTop)
        camerasLayout2.setContentsMargins(0, 0, 0, 0)
        camerasLayout2.setSpacing(0)

        camerasLayout.addLayout(camerasLayout1, stretch=1)
        camerasLayout.addLayout(camerasLayout2, stretch=2)

        # Panel 1 (Section 1): Adding cameras
        self.camerasList = QListWidget(self)
        self.camerasList.setFixedWidth(400)
        self.camerasList.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.camerasList.itemSelectionChanged.connect(self.onCameraSelected)
        camerasLayout1.addWidget(self.camerasList)

        # Define a drop-down menu for selecting calibration file type
        self.calibrationType = QComboBox(self)
        self.calibrationType.addItem("Pose2Sim")
        self.calibrationType.addItem("AniPose")
        self.calibrationType.addItem("bioCV")
        self.calibrationType.addItem("Caliscope")
        self.calibrationType.addItem("EasyMocap")
        self.calibrationType.addItem("FreeMocap")
        self.calibrationType.addItem("OpenCap")
        self.calibrationType.addItem("Optitrack")
        self.calibrationType.addItem("Qualisys")
        self.calibrationType.addItem("Vicon")

        self.calibrationImport = LabeledWidget(
            "Import Calibration File", self.calibrationType
        )
        camerasLayout1.addWidget(self.calibrationImport)
        self.calibrationImport.setFixedWidth(400)
        self.calibrationImport.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

        self.importCalibrationButton = QPushButton("Import File", self)
        self.importCalibrationButton.clicked.connect(self.selectCalibrationFile)
        self.calibrationImport.layout.addWidget(self.importCalibrationButton)

        self.startCalibrationButton = QPushButton("Calibrate Manually", self)
        self.startCalibrationButton.clicked.connect(self.calibrateManually)
        self.calibrationImport.layout.addWidget(self.startCalibrationButton)

        # Panel 1 (Section 2): Modifying calibration parameters
        self.calibrationTabs = TabbedArea(self)
        self.calibrationTabs.tabs.setFixedWidth(400)
        self.calibrationTabs.tabs.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        camerasLayout2.addWidget(self.calibrationTabs)
        camerasLayout2.addStretch()

        # Add tabs for Intrinsic, Extrinsic, and Other
        self.intrinsicTab = Tab("Intrinsic", self.calibrationTabs)
        self.calibrationTabs.addTab(self.intrinsicTab)

        self.extrinsicTab = Tab("Extrinsic", self.calibrationTabs)
        self.calibrationTabs.addTab(self.extrinsicTab)

        self.otherTab = Tab("Other", self.calibrationTabs)
        self.calibrationTabs.addTab(self.otherTab)

    def selectCalibrationFile(self):
        """Open a file dialog to select the TOML calibration file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("TOML File (*.toml)")
        if file_dialog.exec():
            with contextlib.suppress(ValueError):
                selected_file = file_dialog.selectedFiles()[0]
                self.experiment.set_camera_parameters(selected_file)
                self.refreshUI()

    def setExperiment(self, experiment: Experiment):
        self.experiment = experiment
        cameraParameters = self.experiment.get_camera_parameters()
        self.setCameraInfo(cameraParameters)

    def refreshUI(self):
        experiment: Experiment = self.experiment
        cameraParameters = experiment.get_camera_parameters()
        self.updateCalibrationFile(cameraParameters)

    def updateCalibrationFile(self, file_path: str):
        """Display the selected calibration file."""
        if file_path is not None:
            filename = os.path.basename(file_path)
            self.calibrationLabel.setText("Calibration file: " + filename)
            self.importCalibrationButton.setEnabled(False)
        else:
            self.calibrationLabel.setText("No calibration file uploaded")
            self.importCalibrationButton.setEnabled(True)

    def calibrateManually(self):
        # TODO: Get following parameters from the UI
        self.experiment.calibrate_cameras(
            overwrite_intrinsics=True,
            intrinsics_extension="jpg",
            intrinsics_corners_nb=(8, 13),
            intrinsics_square_size=20, # mm
            calculate_extrinsics=False,
        )

        # TODO: Update extrinsics calibration code to not require cv2 windows so that it will work in the UI
        # self.experiment.calibrate_cameras(
        #     overwrite_intrinsics=False,
        #     intrinsics_extension="jpg",
        #     intrinsics_corners_nb=(8, 13),
        #     intrinsics_square_size=20, # mm
        #     calculate_extrinsics=True,
        #     extrinsics_method="board",
        #     extrinsics_extension="jpg",
        #     extrinsics_corners_nb=(8, 13),
        #     extrinsics_square_size=20, # mm
        #     show_reprojection_error=True,
        # )

    def setCameraInfo(self, calib_file):
        if calib_file is None or not os.path.exists(calib_file):
            self.cameras = None
            self.visualizer = None
            self.clearFigure()
            self.camerasList.clear()
            self.camerasList.hide()
            self.calibrationImport.show()
            return

        self.cameras = CameraSystem(calib_file)
        self.visualizer = CameraVisualizer(self.cameras)
        fig = self.visualizer.visualize()
        self.showFigure(fig)

        # Populate the cameras list
        self.camerasList.clear()
        for camera in self.cameras.cameras:
            item = QListWidgetItem(camera.id)
            self.camerasList.addItem(item)
        self.camerasList.show()
        self.calibrationImport.hide()

    def clearFigure(self):
        if self.canvas is not None:
            self.canvas.setParent(None)
            self.canvas.deleteLater()
            self.canvas = None

    def showFigure(self, fig):
        self.clearFigure()
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.canvasLayout.addWidget(self.canvas)

    def onCameraSelected(self):
        selected_items = self.camerasList.selectedItems()
        self.clearCameraDetails()
        if not selected_items:
            return

        selected_camera = selected_items[0].text()
        camera = next(
            (c for c in self.cameras.cameras if c.id == selected_camera), None
        )
        if camera is None:
            return

        # Show camera parameters in the tabs
        intrinsic_params = QVBoxLayout()
        intrinsic_params.setAlignment(Qt.AlignmentFlag.AlignTop)
        for key, value in camera.intrinsic_parameters.items():
            with contextlib.suppress(AssertionError):
                widget = MatrixWidget(self)
                widget.setMatrix(value)
                label = LabeledWidget(key, widget, parent=self)
                intrinsic_params.addWidget(label)
        intrinsic_params.addStretch()
        self.intrinsicTab.addLayout(intrinsic_params)

        extrinsic_params = QVBoxLayout()
        extrinsic_params.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.extrinsicTab.addLayout(extrinsic_params)

        # Rotation matrix
        widget = MatrixWidget(self)
        widget.setMatrix(camera.R_mat)
        label = LabeledWidget("Rotation Matrix", widget, parent=self)
        extrinsic_params.addWidget(label)

        # Translation vector
        widget = MatrixWidget(self)
        widget.setMatrix(camera.translation_vector)
        label = LabeledWidget("Translation Vector", widget, parent=self)
        extrinsic_params.addWidget(label)
        extrinsic_params.addStretch()

        other_params = QLabel(self)
        other_params.setText(
            "Fish eye: "
            + str(camera.fisheye)
            + "\n"
            + "Image size: "
            + str(camera.image_size)
        )
        self.otherTab.addWidget(other_params)

        # Align all tabs to the top
        self.intrinsicTab.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.extrinsicTab.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.otherTab.setAlignment(Qt.AlignmentFlag.AlignTop)

    def clearCameraDetails(self):
        self.intrinsicTab.clear()
        self.extrinsicTab.clear()
        self.otherTab.clear()
