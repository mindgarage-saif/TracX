import logging
import threading

import cv2

from .camera_streams import CameraStreams

logger = logging.getLogger(__name__)


class CameraController:
    def __init__(self):
        self._camera = None
        self._camera_id = None
        self._sources = []
        self._is_started = False
        self.on_camera_changed = lambda: None
        self.on_frame_fn = lambda frame: None
        self.writers = []

    def add_source(self, camera_id, view):
        self._sources.append((camera_id, view))

    def change_camera(self):
        camera_id = [c[0] for c in self._sources]
        logger.info(f"Changing camera to {camera_id}")

        camera_views = [c[1] for c in self._sources]
        for view in camera_views:
            view.clear()
            view.flip = True

        assert all(isinstance(c, int) or c.isdigit() for c in camera_id)
        self._camera_id = camera_id

        self.release()
        self.on_camera_changed()

    def toggle_start(self):
        if self._is_started:
            self.pause()
        else:
            self.change_camera()
            self.start()

    def record(self):
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
            self._camera = CameraStreams(
                self._camera_id,
                sample_rate=None,
                sync_delta=None,
            )

            for cam_id, view in self._sources:
                view.clear()

                self.writers.append(cv2.VideoWriter(
                    f"output_{cam_id}.mp4",
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    self._camera.sample_rate,
                    self._camera.resolution(cam_id)
                ))

            self._camera.on_frame(self.process_multi)
            self._is_started = True
            self._camera.start()

    def pause(self):
        if not self._is_started or self._camera is None:
            return

        self._is_started = False
        
        # Release video writers
        for writer in self.writers:
            writer.release()
        self.writers.clear()

    def process_multi(self, frames):
        """
        Processes multiple video frames by resizing them to the same resolution,
        applying center cropping if their aspect ratios differ, and concatenating them side by side.

        Args:
            frames (Tuple[numpy.ndarray]): The video frames.
        """

        def center_crop(frame, target_aspect_ratio):
            """
            Crops the input frame to the target aspect ratio centered.

            Args:
                frame (numpy.ndarray): The input image frame.
                target_aspect_ratio (float): The desired aspect ratio (width / height).

            Returns:
                numpy.ndarray: The center-cropped frame.
            """
            height, width = frame.shape[:2]
            current_aspect_ratio = width / height

            if current_aspect_ratio > target_aspect_ratio:
                # Crop width
                new_width = int(height * target_aspect_ratio)
                start_x = (width - new_width) // 2
                cropped_frame = frame[:, start_x : start_x + new_width]
            else:
                # Crop height
                new_height = int(width / target_aspect_ratio)
                start_y = (height - new_height) // 2
                cropped_frame = frame[start_y : start_y + new_height, :]

            return cropped_frame

        views = [c[1] for c in self._sources]
        writers = self.writers
        if len(writers) == 0:
            writers = [None] * len(views)
        zipped = list(zip(frames, views, writers))

        # Get shape of the first frame
        h, w = zipped[0][0].shape[:2]

        for i, (frame, view, writer) in enumerate(zipped):
            if frame is None:
                continue

            # Write frame
            if writer is not None:
                writer.write(frame)

            # Center crop the frame to match the aspect ratio of the first frame
            frame_cropped = center_crop(frame, w / h)

            self.process(True, frame_cropped, view)

    def process(self, ret, frame, view):
        # Run this on a worker thread
        threading.Thread(target=self._process, args=(ret, frame, view)).start()

    def _process(self, ret, frame, view):
        if not self._is_started or self._camera is None:
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
