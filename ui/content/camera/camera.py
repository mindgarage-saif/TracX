import os
import cv2
import ktb
from sam2.build_sam import build_sam2_camera_predictor

from .camera_view import CameraView


class Camera:
    def __init__(self, size):
        self._camera = None
        self._camera_id = None
        self._is_started = False
        self._is_video = False
        self._view = CameraView(size, flip=True)
        self._tracker = build_sam2_camera_predictor("sam2_hiera_t.yaml", "assets/sam2_hiera_tiny.pt")
        self._init_tracker = False

    def get_available_cameras(self):
        cameras = []
        for i in range(5):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                cameras.append(i)
                camera.release()
        
        # Add Kinect camera (if available)
        cameras.append("kinect")
        return cameras

    def select_default_camera(self):
        cameras = self.get_available_cameras()
        if len(cameras) > 0:
            self.change_camera(cameras[0])
        else:
            raise Exception("No cameras available")

    def change_camera(self, camera_id):
        print(f"Changing camera to {camera_id}")
        self._is_video = False
        self._init_tracker = False
        if camera_id == "kinect":
            self.release()
            self._camera_id = camera_id
            return

        if isinstance(camera_id, int) or camera_id.isdigit():
            self._camera_id = int(camera_id)
        else:
            # Must be path to a video file
            if not os.path.exists(camera_id):
                raise Exception("Invalid video file path")
            self._camera_id = camera_id
            self._is_video = True

        self.release()

    def toggle_start(self):
        if self._is_started:
            self.pause()
        else:
            self.start()

    def screenshot(self):
        import os
        import time

        user_path = os.path.expanduser("~")
        desktop = os.path.join(user_path, "Desktop")
        path = os.path.join(desktop, f"PPStudio_{time.time()}.jpg")
        self._view.pixmap().save(path)
        return path

    def start(self):
        if self._is_started and self._camera is not None:
            return

        if self._camera is None:
            self._view.clear()
            if self._camera_id == "kinect":
                self._camera = ktb.Kinect()
            else:
                self._camera = cv2.VideoCapture(self._camera_id)

        self._is_started = True

    def pause(self):
        if not self._is_started or self._camera is None:
            return

        self._is_started = False

    def read(self):
        if not self._is_started or self._camera is None:
            return False, None

        if self._camera_id == "kinect":
            color = self._camera.get_frame(ktb.COLOR)
            depth = self._camera.get_frame(ktb.RAW_DEPTH)
            return True, (color, depth)

        return self._camera.read()

    def release(self):
        if self._camera is not None:
            if self._camera_id == "kinect":
                self._camera = None
            else:
                self._camera.release()
                self._camera = None

            self._is_started = False
            self._view.clear()
