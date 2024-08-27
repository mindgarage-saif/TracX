import os
import cv2
import logging

logger = logging.getLogger(__name__)

try:
    import ktb  # https://github.com/nikwl/kinect-toolbox/
    from pylibfreenect2 import Freenect2  # dependency of ktb
except ImportError:
    logger.warning("kinect-toolbox not found, Kinect camera will not work")
    logger.warning("see https://github.com/nikwl/kinect-toolbox/?tab=readme-ov-file#installation")
    ktb = None

from .camera_view import CameraView
from .trackers import SAM2LiveTracker


# Maximum number of cameras supported
# -------------------------------------
# This flag controls how many cameras can be used at the same time. It is arbitrary
# and can be increased if needed. The app looks for up to MAX_CAMERAS cameras and 
# makes them available to the user to select from a dropdown menu.
MAX_CAMERAS = 5


def discover_kinects():
    if ktb is None:
        return []

    fn = Freenect2()
    num_devices = fn.enumerateDevices()
    return [f"Kinect {i}" for i in range(num_devices)]


class Camera:
    def __init__(self, size):
        self._camera = None
        self._camera_id = None
        self._is_started = False
        self._is_video = False
        self._view = CameraView(size, flip=True)
        self._tracker = SAM2LiveTracker()

    def check_camera(self, camera_id):
        if isinstance(camera_id, int) or camera_id.isdigit():
            camera = cv2.VideoCapture(int(camera_id))
            if not camera.isOpened():
                return False
            camera.release()
            return True

        if camera_id == "kinect":
            return ktb is not None

        if isinstance(camera_id, str):
            return os.path.exists(camera_id)

        logger.warning(f"Invalid camera id: {camera_id}")
        return False

    def get_available_cameras(self):
        # Add regular cameras
        cameras = []
        for i in range(MAX_CAMERAS):
            if not self.check_camera(i):
                break
            cameras.append(i)

        # Add kinect cameras
        kinects = discover_kinects()
        cameras.extend(kinects)

        return cameras

    def select_default_camera(self):
        cameras = self.get_available_cameras()
        if len(cameras) > 0:
            self.change_camera(cameras[0])
        else:
            raise Exception("No cameras available")

    def change_camera(self, camera_id):
        logger.info(f"Changing camera to {camera_id}")
        self._is_video = False
        self._view.flip = True
        self._tracker.reset()
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
            self._view.flip = False

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
            if isinstance(self._camera_id, str) and self._camera_id.startswith("Kinect"):
                kinect_id = int(self._camera_id.split(" ")[1])
                self._camera = ktb.Kinect(kinect_id)
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

    def preview(self, frame):
        self._view.show(frame)
