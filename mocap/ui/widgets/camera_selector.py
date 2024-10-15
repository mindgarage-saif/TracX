from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...recording.utils import find_cameras
from ..config.constants import PAD_X, PAD_Y


class CameraItemWidget(QWidget):
    def __init__(self, camera_info: dict, parent: QWidget = None):
        super().__init__(parent)

        # Create a layout for the camera item
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a checkbox to select this camera
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        # Create labels for camera details
        # camera_label = QLabel(
        #     f"{camera_info['manufacturer']} {camera_info['model']} ({camera_info['width']}x{camera_info['height']} @ {camera_info['fps']} FPS)"
        # )
        # camera_label.setProperty("class", "body")
        # camera_label.setWordWrap(True)

        # # Add the camera label to the layout
        # layout.addWidget(camera_label)

        # Add a stretch to push the items to the left
        layout.addStretch()

        self.setLayout(layout)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()


class CameraSelector(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)
        self.setLayout(self.innerLayout)

        # Add a title to the page
        title = QLabel("Select Cameras")
        title.setProperty("class", "h3")
        self.innerLayout.addWidget(title)

        # Add instructions
        instructions = QLabel(
            "Select one or more cameras to record from. If multiple cameras are selected, they will be synchronized."
        )
        instructions.setProperty("class", "body")
        instructions.setWordWrap(True)
        instructions.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        self.innerLayout.addWidget(instructions)
        self.innerLayout.addSpacing(PAD_Y)

        # Show all cameras in a list with checkboxes, allowing multiple selection
        self.camera_list = QListWidget()
        self.camera_list.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding
        )
        self.camera_items = []
        self.innerLayout.addWidget(self.camera_list)
        self.innerLayout.addSpacing(PAD_Y)

        # Add refresh instructions
        refresh_instructions = QLabel(
            "Don't see your camera? Unplug and replug it, then click the refresh button to search again."
        )
        refresh_instructions.setProperty("class", "body")
        refresh_instructions.setWordWrap(True)
        refresh_instructions.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        self.innerLayout.addWidget(refresh_instructions)
        self.innerLayout.addSpacing(16)

        # Create a horizontal button bar
        self.buttonBar = QWidget()
        self.buttonBarLayout = QHBoxLayout(self.buttonBar)
        self.buttonBarLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonBarLayout.setSpacing(16)
        self.innerLayout.addWidget(self.buttonBar)

        # Refresh button
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refresh)
        self.refreshButton.setProperty("class", "secondary_button")
        self.buttonBarLayout.addWidget(self.refreshButton)

        # Add a record button to start recording
        self.recordButton = QPushButton("Select Cameras")
        self.recordButton.clicked.connect(self.record)
        self.buttonBarLayout.addWidget(self.recordButton)

        # Refresh the camera list
        self.createCameraList()

        # Callbacks.
        self.onCamerasSelected = None

    def createCameraList(self):
        self.camera_list.clear()
        self.camera_items = []

        cameras = find_cameras()
        for camera in cameras:
            # Create a custom widget for each camera and wrap it in a QListWidgetItem
            camera_item_widget = CameraItemWidget(camera)
            self.camera_items.append((camera_item_widget, camera))

            # Create a QListWidgetItem to hold the custom widget
            list_item = QListWidgetItem(self.camera_list)
            list_item.setSizeHint(camera_item_widget.sizeHint())
            self.camera_list.addItem(list_item)
            self.camera_list.setItemWidget(list_item, camera_item_widget)

    def refresh(self):
        self.createCameraList()

    def record(self):
        # Collect the selected camera ids
        selected_camera_ids = []
        for camera_item, camera_info in self.camera_items:
            if camera_item.is_selected():
                selected_camera_ids.append(camera_info)

        if not selected_camera_ids:
            # TODO: logger.info("Please select at least one camera to record.")
            return

        if self.onCamerasSelected:
            self.onCamerasSelected(selected_camera_ids)

    def setCameraSelectedCallback(self, callback):
        self.onCamerasSelected = callback
