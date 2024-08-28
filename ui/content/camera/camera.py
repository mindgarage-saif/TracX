import os
import logging

import cv2
import numpy as np
from matplotlib import pyplot as plt

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
        self._tracked_object = []
        self.start_frame = 0
        self.end_frame = -1  # -1 means end of video
        self.current_frame = 0
        self.on_camera_changed = lambda: None

        # Listen to camera view mouse press event
        self._view.mousePressed.connect(self.on_mouse_press)

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

    def on_mouse_press(self, x, y, replace=True):
        if replace:
            self._tracked_object = [[x, y]]
        else:
            self._tracked_object.append([x, y])
        self._tracker.reset()

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
        self.start_frame = 0
        self.end_frame = -1
        self.current_frame = 0
        self.on_camera_changed()

    def get_duration(self):
        if not self._is_video:
            return 0

        video = cv2.VideoCapture(self._camera_id)
        fps = video.get(cv2.CAP_PROP_FPS)
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        video.release()
        return int(frames / fps)

    def get_fps(self):
        if not self._is_video:
            return 0

        video = cv2.VideoCapture(self._camera_id)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        return fps

    def set_start_frame(self, start):
        if not self._is_video:
            return

        fps = self.get_fps()
        start_frame = int(start * fps)
        if start_frame != self.start_frame:
            self.start_frame = start_frame
            self.current_frame = start_frame
            # make sure only these frames are read
            self._camera = cv2.VideoCapture(self._camera_id)
            self._camera.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

            # preview the frame
            ret, frame = self._camera.read()
            self.preview(frame)

            self._camera.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

    def set_end_frame(self, end):
        if not self._is_video:
            return

        end_frame = int(end * self.get_fps())
        if end_frame != self.end_frame:
            self.end_frame = end_frame
          
            # preview the frame
            self._camera = cv2.VideoCapture(self._camera_id)
            self._camera.set(cv2.CAP_PROP_POS_FRAMES, self.end_frame)
            ret, frame = self._camera.read()
            self.preview(frame)
            self._camera.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

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
            return False, None, None

        if self._camera_id == "kinect":
            color = self._camera.get_frame(ktb.COLOR)
            depth = self._camera.get_frame(ktb.RAW_DEPTH)
            return True, (color, depth), None

        if self._is_video:
            self.current_frame += 1
            if self.end_frame != -1 and self.current_frame > self.end_frame:
                self.pause()
                return False, None, None

        ret, frame = self._camera.read()
        if not ret:
            self.pause()
            return False, None, None

        # Resize frame to max 640px on the longest side
        # if self._is_video:
        max_size = 640
        h, w = frame.shape[:2]
        if h > w:
            small_frame = cv2.resize(frame, (max_size, int(h / w * max_size)))
        else:
            small_frame = cv2.resize(frame, (int(w / h * max_size), max_size))

        if not self._tracker.is_init and self._tracked_object:
            def scale(point, w, h):
                return [
                    int(point[0] * small_frame.shape[1] / w),
                    int(point[1] * small_frame.shape[0] / h),
                ]
            scaled_points = [scale(p, w, h) for p in self._tracked_object]
            track_results = self._tracker.init(small_frame, prompt=scaled_points)
            
        else:
            track_results = self._tracker.track(small_frame)

        vis, bbox = self._tracker.visualize(
            small_frame,
            track_results
        )
        vis = cv2.resize(vis, (w, h))
        
        # scale bbox to original frame size
        if bbox is not None:
            bbox = (
                int(bbox[0] * w / small_frame.shape[1]),
                int(bbox[1] * h / small_frame.shape[0]),
                int(bbox[2] * w / small_frame.shape[1]),
                int(bbox[3] * h / small_frame.shape[0]),
            )
        # else:
        #     vis = frame
        #     bbox = None

        return True, frame, (vis, bbox)

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
