from PyQt6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
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


        # Show all cameras in a list with checkboxes, allowing multiple selection
        self.camera_list = QListWidget()
        self.camera_items = []
        self.innerLayout.addWidget(self.camera_list)
        
        # Add a record button to start recording
        self.recordButton = QPushButton("Start Recording")
        self.recordButton.clicked.connect(self.record)
        self.innerLayout.addWidget(self.recordButton)

        # Refresh button
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refresh)
        self.innerLayout.addWidget(self.refreshButton)

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
