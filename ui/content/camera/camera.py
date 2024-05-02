import cv2

from .camera_view import CameraView


class Camera:
    def __init__(self, size, camera_id=0):
        self._camera = None
        try:
            self._camera_id = int(camera_id)
        except ValueError:
            self._camera_id = camera_id
        self._is_started = False
        self._view = CameraView(size, flip=isinstance(camera_id, int))

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
        if self._is_started:
            return

        if self._camera is None:
            self._view.clear()
            self._camera = cv2.VideoCapture(self._camera_id)

        self._is_started = True

    def pause(self):
        if not self._is_started:
            return

        self._is_started = False

    def read(self):
        if not self._is_started:
            return False, None

        return self._camera.read()

    def release(self):
        if self._camera is not None:
            self._camera.release()
            self._camera = None
            self._is_started = False
            self._view.clear()
