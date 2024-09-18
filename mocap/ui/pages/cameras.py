from PyQt6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from ...recording.utils import find_cameras
from .base import BasePage


class CameraItemWidget(QWidget):
    def __init__(self, camera_info: dict, parent: QWidget = None):
        super().__init__(parent)

        # Create a layout for the camera item
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Create a checkbox to select this camera
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        # Create labels for camera details
        camera_label = QLabel(f"[CAM {camera_info['id']}] {camera_info['manufacturer']} {camera_info['model']} ({camera_info['width']}x{camera_info['height']} @ {camera_info['fps']} FPS)")
        camera_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-left: 5px;")
        
        # Add the camera label to the layout
        layout.addWidget(camera_label)

        # Add a stretch to push the items to the left
        layout.addStretch()

        self.setLayout(layout)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()


class CameraSelectionPage(BasePage):
    def __init__(self, context: QWidget, parent: QWidget) -> None:
        super().__init__(context, parent)

        self.container = QWidget()
        self.innerLayout.addWidget(self.container)
        self.containerLayout = QVBoxLayout(self.container)
        self.containerLayout.setContentsMargins(8, 0, 8, 0)
        self.containerLayout.setSpacing(16)
        self.container.setLayout(self.containerLayout)

        # Add a title to the page
        title = QLabel("Select Cameras")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.containerLayout.addWidget(title)

        # Add instructions
        instructions = QLabel("Select one or more cameras to record from. If multiple cameras are selected, they will be synchronized.")
        instructions.setStyleSheet("font-size: 16px;")
        self.containerLayout.addWidget(instructions)

        # Show all cameras in a list with checkboxes, allowing multiple selection
        self.camera_list = QListWidget()
        self.camera_list.setFixedWidth(parent.width() - 16 * 4 - 4)
        self.camera_items = []
        self.containerLayout.addWidget(self.camera_list)
        
        # Add refresh instructions
        refresh_instructions = QLabel("Don't see your camera? Unplug and replug it, then click the refresh button to search again.")
        refresh_instructions.setStyleSheet("font-size: 14px;")
        self.containerLayout.addWidget(refresh_instructions)

        # Create a horizontal button bar
        self.buttonBar = QWidget()
        self.buttonBarLayout = QHBoxLayout(self.buttonBar)
        self.buttonBarLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonBarLayout.setSpacing(16)
        self.containerLayout.addWidget(self.buttonBar)

        # Add a record button to start recording
        self.recordButton = QPushButton("Start Recording")
        self.recordButton.clicked.connect(self.record)
        self.buttonBarLayout.addWidget(self.recordButton)

        # Refresh button
        self.refreshButton = QPushButton("Refresh Cameras")
        self.refreshButton.clicked.connect(self.refresh)
        self.refreshButton.setProperty("class", "secondary_button")
        self.buttonBarLayout.addWidget(self.refreshButton)

        # Refresh the camera list
        self.createCameraList()

        # Add stretch to push the list to the top
        self.innerLayout.addStretch()

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
            self.log("Please select at least one camera to record.")
            return

        # Pass selected camera IDs to the next page
        self.context.changePage("record", cameras=selected_camera_ids)
