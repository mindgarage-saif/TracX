import os

import cv2
import ktb
import numpy as np
from matplotlib import pyplot as plt
from sam2.build_sam import build_sam2_camera_predictor

from .camera_view import CameraView


class Camera:
    def __init__(self, size):
        self._camera = None
        self._camera_id = None
        self._is_started = False
        self._is_video = False
        self._view = CameraView(size, flip=True)
        self._tracker = build_sam2_camera_predictor(
            "sam2_hiera_t.yaml", "assets/sam2_hiera_tiny.pt"
        )
        self._tracked_object = None
        self._init_tracker = False
        self.start_frame = 0
        self.end_frame = -1  # -1 means end of video
        self.current_frame = 0
        self.on_camera_changed = lambda: None

        # Listen to camera view mouse press event
        self._view.mousePressed.connect(self.on_mouse_press)

    def on_mouse_press(self, x, y):
        self._tracked_object = [x, y]
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
            if self._camera_id == "kinect":
                self._camera = ktb.Kinect()
            else:
                self._camera = cv2.VideoCapture(self._camera_id)

        self._is_started = True

    def pause(self):
        if not self._is_started or self._camera is None:
            return

        self._is_started = False

    def show_mask(self, mask, frame, obj_id=None, random_color=False):
        if random_color:
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        else:
            cmap = plt.get_cmap("tab10")
            cmap_idx = 0 if obj_id is None else obj_id
            color = np.array([*cmap(cmap_idx)[:3], 0.6])
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)  # in [0, 1]

        # add alpha channel in frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)  # in [0, 255]

        frame = frame.astype(np.float32) / 255.0
        frame = frame * (1 - mask_image) + mask_image
        frame = (frame * 255).astype(np.uint8)

        # remove alpha channel, merge with original frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        return frame

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
        if self._is_video:
            max_size = 640
            h, w = frame.shape[:2]
            if h > w:
                small_frame = cv2.resize(frame, (max_size, int(h / w * max_size)))
            else:
                small_frame = cv2.resize(frame, (int(w / h * max_size), max_size))

            if not self._init_tracker and self._tracked_object is not None:
                self._tracker.load_first_frame(small_frame)
                point = self._tracked_object
                scaled_point = [
                    int(point[0] * small_frame.shape[1] / w),
                    int(point[1] * small_frame.shape[0] / h),
                ]
                self._init_tracker = True
                _, out_obj_ids, out_mask_logits = self._tracker.add_new_prompt(
                    frame_idx=0,
                    obj_id=0,
                    points=np.array([scaled_point], dtype=np.float32),
                    labels=np.array([1], np.int32),
                )

            else:
                out_obj_ids, out_mask_logits = self._tracker.track(small_frame)

            masked_frame = self.show_mask(
                (out_mask_logits[0] > 0.0).cpu().numpy(),
                small_frame.copy(),
                obj_id=out_obj_ids[0],
            )

            # Upscale the masked frame to the original size
            masked_frame = cv2.resize(masked_frame, (w, h))

            # Get bounding box from mask
            mask = out_mask_logits[0] > 0.0
            mask = mask.cpu().numpy().astype(np.uint8)[0]
            mask = cv2.resize(mask, (w, h))

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if len(contours) > 0:
                bboxes = [cv2.boundingRect(c) for c in contours]
                x = min([bbox[0] for bbox in bboxes])
                y = min([bbox[1] for bbox in bboxes])
                w = max([bbox[0] + bbox[2] for bbox in bboxes]) - x
                h = max([bbox[1] + bbox[3] for bbox in bboxes]) - y
                bbox = (x, y, w, h)
            else:
                bbox = None

        else:
            masked_frame = frame
            bbox = None

        return True, frame, (masked_frame, bbox)

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
