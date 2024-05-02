import os
import cv2

from .camera_view import CameraView


class Camera:
    def __init__(self, size):
        self._camera = None
        self._camera_id = None
        self._is_started = False
        self._view = CameraView(size, flip=True)

    def get_available_cameras(self):
        cameras = []
        for i in range(5):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                cameras.append(i)
                camera.release()
        return cameras

    def select_default_camera(self):
        cameras = self.get_available_cameras()
        if len(cameras) > 0:
            self.change_camera(cameras[0])
        else:
            raise Exception("No cameras available")

    def change_camera(self, camera_id):
        print(f"Changing camera to {camera_id}")
        if isinstance(camera_id, int) or camera_id.isdigit():
            self._camera_id = int(camera_id)
        else:
            # Must be path to a video file
            if not os.path.exists(camera_id):
                raise Exception("Invalid video file path")
            self._camera_id = camera_id

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
            self._camera = cv2.VideoCapture(self._camera_id)

        self._is_started = True

    def pause(self):
        if not self._is_started or self._camera is None:
            return

        self._is_started = False

    def read(self):
        if not self._is_started or self._camera is None:
            return False, None

        return self._camera.read()

    def release(self):
        if self._camera is not None:
            self._camera.release()
            self._camera = None
            self._is_started = False
            self._view.clear()
