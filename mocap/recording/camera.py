import logging
import threading

from .stereo_capture import StereoCapture
from .synchronized_capture import SynchronizedCapture
from .video import VideoCapture

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self):
        self._camera = None
        self._camera_id = None
        self._sources = []
        self._is_started = False
        self._is_video = False
        self.start_frame = 0
        self.end_frame = -1  # -1 means end of video
        self.current_frame = 0
        self.on_camera_changed = lambda: None
        self.on_frame_fn = lambda frame: None
        self.calibration_mode = False
        self.calibration_frames = []
        self.max_calibration_frames = 100

    def add_source(self, camera_id, view):
        self._sources.append((camera_id, view))

    def change_camera(self):
        # self._is_video = False

        camera_id = [c[0] for c in self._sources]
        logger.info(f"Changing camera to {camera_id}")

        camera_views = [c[1] for c in self._sources]
        for view in camera_views:
            view.clear()
            view.flip = True

        assert all(isinstance(c, int) or c.isdigit() for c in camera_id)
        self._camera_id = camera_id

        # # Must be path to a video file
        # if not os.path.exists(camera_id):
        #     raise Exception("Invalid video file path")
        # self._camera_id = camera_id
        # self._is_video = True
        # self._view.flip = False

        self.release()
        self.start_frame = 0
        self.end_frame = -1
        self.current_frame = 0
        self.on_camera_changed()

    def toggle_start(self):
        if self._is_started:
            self.pause()
        else:
            self.change_camera()
            self.start()

    def screenshot(self):
        import os
        import time

        user_path = os.path.expanduser("~")
        desktop = os.path.join(user_path, "Desktop")
        path = os.path.join(desktop, f"PPStudio_{time.time()}.jpg")
        views = [c[1] for c in self._sources]
        for i, view in enumerate(views):
            view_path = path.replace(".jpg", f"_{i}.jpg")
            view.pixmap().save(view_path)
        return path

    def start(self):
        if self._is_started and self._camera is not None:
            return

        if self._camera is None and self._camera_id is not None:
            for view in [c[1] for c in self._sources]:
                view.clear()
            if isinstance(self._camera_id, list) or isinstance(self._camera_id, tuple):
                print("Setting up multiple cameras")
                self._camera = SynchronizedCapture(
                    self._camera_id, sample_rate=24, max_frames=-1
                )
                self._camera.on_frame_captured(self.process_multi)
                self._is_started = True
                self._camera.start()
            else:
                print("Setting up video capture")
                self._camera = VideoCapture(self._camera_id)
                self._camera.on_frame_captured(self.process)
                self._is_started = True
                self._camera.start()

    def pause(self):
        if not self._is_started or self._camera is None:
            return

        self._is_started = False

    def process_multi(self, frames):
        """
        Processes multiple video frames by resizing them to the same resolution,
        applying center cropping if their aspect ratios differ, and concatenating them side by side.

        Args:
            frames (Tuple[numpy.ndarray]): The video frames.
        """
        print("Processing frames", len(frames))
        views = [c[1] for c in self._sources]
        zipped = list(zip(frames, views))
        for i, (frame, view) in enumerate(zipped):
            if frame is None:
                continue
            self.process(True, frame, view)

        # def center_crop(frame, target_aspect_ratio):
        #     """
        #     Crops the input frame to the target aspect ratio centered.

        #     Args:
        #         frame (numpy.ndarray): The input image frame.
        #         target_aspect_ratio (float): The desired aspect ratio (width / height).

        #     Returns:
        #         numpy.ndarray: The center-cropped frame.
        #     """
        #     height, width = frame.shape[:2]
        #     current_aspect_ratio = width / height

        #     if current_aspect_ratio > target_aspect_ratio:
        #         # Crop width
        #         new_width = int(height * target_aspect_ratio)
        #         start_x = (width - new_width) // 2
        #         cropped_frame = frame[:, start_x : start_x + new_width]
        #     else:
        #         # Crop height
        #         new_height = int(width / target_aspect_ratio)
        #         start_y = (height - new_height) // 2
        #         cropped_frame = frame[start_y : start_y + new_height, :]

        #     return cropped_frame

        # # Get original dimensions
        # h1, w1 = frame1.shape[:2]
        # h2, w2 = frame2.shape[:2]

        # # Calculate aspect ratios
        # aspect1 = w1 / h1
        # aspect2 = w2 / h2

        # # Determine the common aspect ratio (use the smaller one to ensure both frames fit)
        # common_aspect_ratio = min(aspect1, aspect2)

        # # Apply center cropping to both frames to match the common aspect ratio
        # frame1_cropped = center_crop(frame1, common_aspect_ratio)
        # frame2_cropped = center_crop(frame2, common_aspect_ratio)

        # # After cropping, get the new dimensions
        # h1_cropped, w1_cropped = frame1_cropped.shape[:2]
        # h2_cropped, w2_cropped = frame2_cropped.shape[:2]

        # # Determine the target size (use the smallest height and width to maintain consistency)
        # target_height = min(h1_cropped, h2_cropped)
        # target_width = min(w1_cropped, w2_cropped)

        # # Resize both frames to the target size
        # frame1_resized = cv2.resize(
        #     frame1_cropped, (target_width, target_height), interpolation=cv2.INTER_AREA
        # )
        # frame2_resized = cv2.resize(
        #     frame2_cropped, (target_width, target_height), interpolation=cv2.INTER_AREA
        # )

        # # Save calibration frames if in calibration mode
        # if self.calibration_mode:
        #     if len(self.calibration_frames) < self.max_calibration_frames:
        #         self.calibration_frames.append((frame1_resized, frame2_resized))
        #     else:
        #         self.calibration_mode = False
        #         try:
        #             calibration = Calibration()
        #             calibration.calibrate(self.calibration_frames)
        #         except Exception as e:
        #             logger.error(f"Calibration failed: {e}")
        #         logger.info("Calibration frames saved")
        #         return

        # # Concatenate the frames horizontally (side by side)
        # concatenated_frame = cv2.hconcat([frame1_resized, frame2_resized])

        # # Send the concatenated frame for processing
        # self.process(True, concatenated_frame)

    def calibrate(self, delay=5, max_frames=100):
        self.calibration_frames = []
        self.max_calibration_frames = max_frames

        # Enable calibration mode after the specified delay (non-blocking)
        def enable_calibration():
            import time

            time.sleep(delay)
            self.calibration_mode = True
            logger.info("Calibration mode enabled")

        threading.Thread(target=enable_calibration).start()

    def process(self, ret, frame, view):
        # Run this on a worker thread
        threading.Thread(target=self._process, args=(ret, frame, view)).start()

    def _process(self, ret, frame, view):
        if not self._is_started or self._camera is None:
            return

        if self._is_video:
            self.current_frame += 1
            if self.end_frame != -1 and self.current_frame > self.end_frame:
                self.pause()
                return

        if not ret:
            self.pause()
            return

        if frame is None:
            return

        if self.on_frame_fn is not None:
            frame = self.on_frame_fn(frame)

        view.show(frame)

    def release(self):
        if self._camera is not None:
            self._camera.release()
            self._camera = None

            self._is_started = False
            for view in [c[1] for c in self._sources]:
                view.clear()
