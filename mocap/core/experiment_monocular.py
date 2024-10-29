import os
import shutil
from typing import Optional

import cv2
import onnxruntime as ort
import toml
import torch
from easydict import EasyDict as edict

from mocap.constants import APP_ASSETS, APP_PROJECTS, SUPPORTED_VIDEO_FORMATS
from mocap.core.monocular_pipeline import estimation_2d, estimation_3d
from mocap.rendering import StickFigureRenderer

from .motion import MotionSequence
from .rotation import rotate_video_monocular


class ExperimentMonocular:
    def __init__(
        self,
        name,
        create=True,
        base_dir=APP_PROJECTS,
        model_path=r"basline_model_MB.onnx",
    ) -> None:
        self.name = name
        self.path = os.path.abspath(os.path.join(base_dir, name))
        self.videos_dir = os.path.join(self.path, "videos")
        self.pose2d_dir = os.path.join(self.path, "pose")
        self.pose3d_dir = os.path.join(self.path, "pose-3d")
        self.config_file = os.path.join(self.path, "Config.toml")
        self.output_dir = os.path.join(self.path, "output")

        model_path = os.path.join(APP_ASSETS, model_path)
        self.MODEL = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )
        self.calibration_dir = os.path.join(self.path, "calibration")
        self.calibration_file = os.path.join(
            self.calibration_dir,
            "camera_parameters.qca.txt",
        )
        try:
            if (
                torch.cuda.is_available()
                and "CUDAExecutionProvider" in ort.get_available_providers()
            ):
                self.device = "cuda"
                self.backend = "onnxruntime"
            else:
                raise
        except:
            try:
                if (
                    "MPSExecutionProvider" in ort.get_available_providers()
                    or "CoreMLExecutionProvider" in ort.get_available_providers()
                ):
                    self.device = "mps"
                    self.backend = "onnxruntime"
                else:
                    raise
            except:
                self.device = "cpu"
                self.backend = "openvino"

        if create:
            try:
                # Create the project directories.
                self._makedirs()

                # Copy the default configuration file.
                default_config = os.path.join(APP_ASSETS, "defaults", "Config.toml")
                shutil.copy(default_config, self.config_file)
            except Exception:
                raise ValueError(f"Project '{name}' already exists.")
        elif not os.path.exists(self.config_file):
            raise ValueError(f"Project '{name}' is missing configuration file.")

        # Read the configuration file.
        self.cfg = toml.load(self.config_file)
        self.cfg = edict(self.cfg)

    @staticmethod
    def list():
        return sorted(
            [
                name
                for name in os.listdir(APP_PROJECTS)
                if os.path.isdir(os.path.join(APP_PROJECTS, name))
            ],
        )

    @staticmethod
    def open(name):
        return Experiment(name, create=False)

    @staticmethod
    def from_path(path):
        return Experiment(
            os.path.basename(path),
            create=False,
            base_dir=os.path.dirname(path),
        )

    def _makedirs(self):
        os.makedirs(self.path)
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.pose2d_dir, exist_ok=True)
        os.makedirs(self.pose3d_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def videos(self) -> list:
        os.makedirs(self.videos_dir, exist_ok=True)
        return [
            os.path.join(self.videos_dir, name)
            for name in sorted(os.listdir(self.videos_dir))
            if os.path.isfile(os.path.join(self.videos_dir, name))
            and os.path.splitext(name)[-1].lower() in SUPPORTED_VIDEO_FORMATS
        ]

    @property
    def num_videos(self):
        return len(self.videos)

    def add_video(self, video_path, move=False) -> bool:
        video_name = os.path.basename(video_path)
        video_fmt = os.path.splitext(video_name)[-1].lower()
        if video_fmt not in SUPPORTED_VIDEO_FORMATS:
            return False

        video_dest = os.path.join(self.videos_dir, video_name)
        if move:
            os.rename(video_path, video_dest)
        else:
            shutil.copy(video_path, video_dest)

        return True

    def has_videos(self):
        return self.num_videos > 0

    def get_camera_parameters(self):
        return self.calibration_file if os.path.exists(self.calibration_file) else None

    def process_monocular(self, mode, correct_rotation, rotation):
        if correct_rotation:
            rotated_dir = os.path.join(self.path, self.videos_dir + "_rotated")
            if not os.path.exists(rotated_dir):
                rotate_video_monocular(self.videos, rotated_dir, rotation)
            else:
                print("Rotated videos already exist. Skipping rotation...")

            # Rename the videos directories to use the rotated videos
            if os.path.exists(self.videos_dir) and os.path.exists(rotated_dir):
                os.rename(self.videos_dir, self.videos_dir + "_original")
                os.rename(rotated_dir, self.videos_dir)
        video_list = os.listdir(self.videos_dir)
        video_path = os.path.join(self.videos_dir, video_list[0])
        print(mode)
        res_w, res_h, fps = estimation_2d(
            video_path,
            mode,
            self.pose2d_dir,
            self.device,
            self.backend,
        )
        estimation_3d(self.pose2d_dir, self.pose3d_dir, self.MODEL, res_w, res_h)

    def get_motion_file(self) -> Optional[str]:
        pose_3d = [f for f in os.listdir(self.pose3d_dir) if f.endswith("data.json")]
        if len(pose_3d) == 0:
            return None
        return os.path.join(self.pose3d_dir, pose_3d[0])

    @property
    def log_file(self):
        return os.path.join(self.path, "logs.log")

    def _visualize_naive(self, motion_file):
        # Create a side-by-side visualization using OpenCV
        # path = os.path.join(self.output_dir, "animation.mp4")

        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if os.path.exists(animation_file):
            return animation_file

        # Find FPS of the first camera video
        video_file = self.videos[0]
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()

        # Create the visualization
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        motion_data = MotionSequence.from_monocular_json(motion_file, fps)
        renderer = StickFigureRenderer(
            motion_data,
            animation_file,
            monocular=True,
            elev=-165,
            azim=155,
            vertical_axis="y",
        )
        renderer.render()

        return animation_file

        # # Read the animation video
        # anim = cv2.VideoCapture(animation_file)

        # # Read the original video
        # video = cv2.VideoCapture(video_file)

        # # Get the video dimensions
        # width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # size = (width * 2, height)

        # # Create the output video
        # out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

        # while True:
        #     ret1, frame1 = video.read()
        #     ret2, frame2 = anim.read()

        #     if not ret1 or not ret2:
        #         break

        #     frame1 = cv2.resize(frame1, (width, height))
        #     frame2 = cv2.resize(frame2, (width, height))

        #     # Concatenate the frames
        #     frame = cv2.hconcat([frame1, frame2])

        #     # Write the frame
        #     out.write(frame)

        # # Release the video objects
        # video.release()
        # anim.release()
        # out.release()

        # return path

    def _visualize_mesh(self, motion_file):
        raise NotImplementedError("OpenSim visualization is not yet supported.")

    def _visualize_mixamo(self, motion_file):
        raise NotImplementedError("OpenSim visualization is not yet supported.")

    def _visualize_opensim(self, motion_file, with_blender=False):
        raise NotImplementedError("OpenSim visualization is not yet supported.")

    def visualize(self, mode="naive", **kwargs):
        """Visualize the results of the experiment.

        Args:
            mode (str): The visualization mode. Supported modes include ['naive', 'mesh', mixamo', 'opensim'].
            **kwargs: Additional keyword arguments to pass to the visualization function for the selected mode.
                      See the documentation of the corresponding visualization function for more details.

        """
        motion_file = self.get_motion_file()
        if motion_file is None:
            raise ValueError(
                "Call the .process() method first before visualizing the results.",
            )

        # Check the visualization mode
        supported_modes = ["naive", "mesh", "mixamo", "opensim"]
        if mode == "naive":
            return self._visualize_naive(motion_file, **kwargs)
        elif mode == "mesh":
            return self._visualize_mesh(motion_file, **kwargs)
        elif mode == "mixamo":
            return self._visualize_mixamo(motion_file, **kwargs)
        elif mode == "opensim":
            return self._visualize_opensim(motion_file, **kwargs)
        else:
            raise ValueError(
                f"Unsupported visualization mode '{mode}'. Use one of {supported_modes}",
            )

    def __str__(self):
        return f"Experiment(name={self.name}, path={self.path})"
