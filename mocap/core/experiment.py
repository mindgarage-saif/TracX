import json
import logging
import os
import shutil
from datetime import datetime
from distutils.dir_util import copy_tree
from typing import Optional

import cv2
import toml
from easydict import EasyDict as edict
from Pose2Sim import Pose2Sim
from Pose2Sim.Utilities import bodykin_from_mot_osim

from mocap.constants import (
    APP_ASSETS,
    APP_PROJECTS,
    OPENSIM_DIR,
    SUPPORTED_VIDEO_FORMATS,
)
from mocap.core.triangulation import triangulate_all
from mocap.rendering import StickFigureRenderer, create_opensim_vis

from .motion import MotionSequence
from .pose import PoseTracker2D, lift_to_3d
from .rotation import rotate_videos, unrotate_pose2d


class Experiment:
    META_FILE = os.path.join(APP_PROJECTS, "db.json")

    def __init__(
        self,
        name,
        create=False,
        monocular=False,
        multi_person=False,
        is_2d=False,
        base_dir=APP_PROJECTS,
    ) -> None:
        self.name = name
        self.path = os.path.abspath(os.path.join(base_dir, name))
        self.config_file = os.path.join(self.path, "Config.toml")
        self.videos_dir = os.path.join(self.path, "videos")
        self.pose2d_dir = os.path.join(self.path, "pose")
        self.pose3d_dir = os.path.join(self.path, "pose-3d")
        self.output_dir = os.path.join(self.path, "output")
        self.calibration_dir = os.path.join(self.path, "calibration")
        self.calibration_file = os.path.join(
            self.calibration_dir,
            "Calib_board.toml",
        )
        self.config_file = os.path.join(self.path, "Config.toml")

        if create:
            try:
                # Set the experiment flags
                self.monocular = monocular
                self.multi_person = multi_person
                self.is_2d = is_2d

                # Create the project directories.
                self._makedirs()

                # Save the metadata
                self.save_metadata()
            except Exception:
                raise ValueError(f"Experiment with name '{name}' already exists.")
        else:
            # Find experiment in the database
            experiments = Experiment.list()
            experiment = next((e for e in experiments if e["name"] == name), None)
            if experiment is None:
                raise ValueError(f"No experiment with name '{name}' found.")

            # Read flags
            self.monocular = experiment.get("monocular", False)
            self.is_2d = experiment.get("is_2d", False)
            self.multi_person = experiment.get("multi_person", False)
            self.created_at = experiment.get("created_at", None)

            # Set the project directories
            self._makedirs(exist_ok=True)

        # Read the configuration file.
        self.cfg = toml.load(self.config_file)
        self.cfg = edict(self.cfg)

    def save_metadata(self):
        metadata = Experiment.list()
        if any(m["name"] == self.name for m in metadata):
            return

        metadata.append(
            {
                "name": self.name,
                "monocular": self.monocular,
                "is_2d": self.is_2d,
                "multi_person": self.multi_person,
                "created_at": str(datetime.now()),
            }
        )

        with open(Experiment.META_FILE, "w") as f:
            json.dump(metadata, f)

    @staticmethod
    def list():
        if not os.path.exists(Experiment.META_FILE):
            with open(Experiment.META_FILE, "w") as f:
                json.dump([], f)

        with open(Experiment.META_FILE) as f:
            db = json.load(f)

        # Read metadata
        metadata = []
        for exp in sorted(db, key=lambda x: x["name"]):
            metadata.append(
                {
                    "name": exp["name"],
                    "monocular": exp.get("monocular", False),
                    "is_2d": exp.get("is_2d", False),
                    "multi_person": exp.get("multi_person", False),
                    "created_at": exp.get("created_at", None),
                    "path": os.path.join(APP_PROJECTS, exp["name"]),
                }
            )

        return metadata

    @staticmethod
    def open(name):
        logging.info(f"Opening experiment '{name}'...")
        return Experiment(name, create=False)

    @staticmethod
    def from_path(path):
        return Experiment(
            os.path.basename(path),
            create=False,
            base_dir=os.path.dirname(path),
        )

    def _makedirs(self, exist_ok=False):
        # Create the project directories.
        os.makedirs(self.path, exist_ok=exist_ok)
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.pose2d_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        if not self.is_2d:
            os.makedirs(self.pose3d_dir, exist_ok=True)
        if not self.monocular:
            os.makedirs(self.calibration_dir, exist_ok=True)

        # Copy the default configuration file.
        if not os.path.exists(self.config_file):
            self.copy_default_config()

    def copy_default_config(self):
        if self.is_2d:
            default_config = os.path.join(APP_ASSETS, "defaults", "Config_Mono2d.toml")
        elif self.monocular:
            default_config = os.path.join(APP_ASSETS, "defaults", "Config_Mono3d.toml")
        else:
            default_config = os.path.join(APP_ASSETS, "defaults", "Config_Multi3d.toml")
        shutil.copy(default_config, self.config_file)

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

    def set_camera_parameters(self, params_file):
        if params_file.split(".")[-1].lower() != "toml":
            raise ValueError(
                "Invalid calibration file format. We except a calibration file in toml format.",
            )

        shutil.copy(params_file, self.calibration_file)

    def get_camera_parameters(self):
        return self.calibration_file if os.path.exists(self.calibration_file) else None

    def update_config(self, cfg):
        def merge_dicts(d1, d2):
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    merge_dicts(d1[key], value)
                else:
                    d1[key] = value
            return d1

        self.cfg = merge_dicts(self.cfg, cfg)
        with open(self.config_file, "w") as f:
            toml.dump(cfg, f)

    def change_config(self, mode, skeleton, trackedpoint):
        file = toml.load(self.config_file)
        file["pose"]["pose_model"] = skeleton
        file["pose"]["mode"] = mode
        file["personAssociation"]["single_person"]["tracked_keypoint"] = trackedpoint
        with open(self.config_file, "w") as f:
            toml.dump(file, f)

        # Update the self.cfg attribute
        self.cfg = toml.load(self.config_file)

    def process(self, cfg):
        # Change the working directory to the project directory.
        cwd = os.getcwd()
        os.chdir(self.path)

        # Update the configuration file with selected settings
        if not self.has_videos():
            raise ValueError("No videos found in the project directory.")

        correct_rotation = cfg.get("correct_rotation", False)
        if correct_rotation and not self.monocular:
            rotated_dir = os.path.join(self.path, self.videos_dir + "_rotated")
            if not os.path.exists(rotated_dir):
                rotate_videos(self.videos, rotated_dir, self.calibration_file)
            else:
                logging.info("Rotated videos already exist. Skipping rotation...")

            # Rename the videos directories to use the rotated videos
            if os.path.exists(self.videos_dir) and os.path.exists(rotated_dir):
                os.rename(self.videos_dir, self.videos_dir + "_original")
                os.rename(rotated_dir, self.videos_dir)

        # Set video format and overwrite flag
        # TODO: Read these from self.cfg
        videos_format = os.path.splitext(self.videos[0])[-1].lower()
        overwrite = False

        # Execute the 2D pose estimation
        logging.info("Executing 2D pose estimatioan...")
        res_w, res_h = 0, 0
        if cfg.pose.pose_model in ["COCO_17", "COCO_133", "HALPE_26"]:
            PoseTracker2D.estimateDefault()
        elif cfg.pose.pose_model == "DFKI_BODY43":
            res_w, res_h, _ = PoseTracker2D.estimateBodyWithSpine(
                videos=self.videos_dir,
                save_dir=self.pose2d_dir,
                video_format=videos_format,
                overwrite=overwrite,
            )
        else:
            raise ValueError(f"Unsupported custom pose model '{cfg.pose2d_model}'")

        # Unrotate the 2D poses
        if correct_rotation:
            # Restore the original videos
            os.rename(self.videos_dir, self.videos_dir + "_rotated")
            os.rename(self.videos_dir + "_original", self.videos_dir)

            logging.info("Rotating 2D poses back...")
            unrotate_pose2d(self.pose2d_dir, self.calibration_file)

        # TODO: Person association should be moved here

        # 2D-to-3D Lifting in Monocular Mode
        if self.monocular:
            logging.info("Lifting 2D poses to 3D...")
            if cfg.pose3d_model == "baseline":
                if res_w == 0 or res_h == 0:
                    raise ValueError(
                        "Invalid resolution. Something went wrong during 2D pose estimation."
                    )

                # Lift the 2D poses to 3D
                model_path = os.path.join(
                    APP_ASSETS, "models", "lifting", "baseline.onnx"
                )
                video_pose_dir = os.path.join(
                    self.pose2d_dir,
                    os.path.basename(self.videos[0]).split(".")[0] + "_json",
                )
                lift_to_3d(model_path, video_pose_dir, self.pose3d_dir, res_w, res_h)
            else:
                raise ValueError(f"Unsupported lifting model '{cfg.lifting_model}'")

        # Triangulation in Multiview Mode
        else:
            # logging.info("Calibrating cameras...")
            # Pose2Sim.calibration()

            logging.info("Finding the most prominent person...")
            Pose2Sim.personAssociation()

            # TODO: Wrap triangulation in a try-except block and throw a nice error message
            logging.info("Triangulating 3D poses...")
            triangulate_all(self)

            logging.info("Smoothing triangulated poses...")
            Pose2Sim.filtering()

        # TODO: Filtering should be moved here

        # Restore the working directory
        os.chdir(cwd)

    def get_motion_file(self) -> Optional[str]:
        if self.is_2d:
            logging.error("Not implemented for 2D experiments.")
            return None

        # 3D Monocular
        if self.monocular:
            pose_3d = [
                f for f in os.listdir(self.pose3d_dir) if f.endswith("data.json")
            ]
            if len(pose_3d) == 0:
                logging.error("No 3D pose data found for monocular experiment.")
                return None
            return os.path.join(self.pose3d_dir, pose_3d[0])

        # 3D Multiview
        trc_files = [
            f
            for f in os.listdir(self.pose3d_dir)
            if f.endswith("_filt_butterworth.trc")
        ]
        if len(trc_files) == 0:
            logging.error("No TRC files found for multiview experiment.")
            return None
        return os.path.join(self.pose3d_dir, trc_files[0])

    @property
    def log_file(self):
        return os.path.join(self.path, "logs.log")

    def read_skeleton(self):
        file = toml.load(self.config_file)
        return file["pose"]["pose_model"]

    def _visualize_naive(self, motion_file):
        # Create a side-by-side visualization using OpenCV
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if os.path.exists(animation_file):
            return animation_file

        # Find FPS of the first camera video
        video_file = self.videos[0]
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        skeleton = self.read_skeleton()

        # Create the visualization
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if self.monocular:
            logging.info("Rendering monocular motion sequence...")
            motion_data = MotionSequence.from_monocular_json(motion_file, fps)
            renderer = StickFigureRenderer(
                motion_data,
                animation_file,
                monocular=True,
                elev=-165,
                azim=155,
                vertical_axis="y",
            )
        else:
            logging.info("Rendering multiview motion sequence...")
            motion_data = MotionSequence.from_pose2sim_trc(motion_file, skeleton)
            renderer = StickFigureRenderer(motion_data, animation_file)
        renderer.render(fps=fps)

        return animation_file

    def _visualize_opensim(self, motion_file, with_blender=False):
        copy_tree(
            os.path.join(OPENSIM_DIR, "..", "Geometry"),
            os.path.join(self.output_dir, "Geometry"),
        )
        output, mot, scaled_model = create_opensim_vis(
            trc=motion_file,
            experiment_dir=self.path,
            scaling_time_range=[0.5, 1.0],
            ik_time_range=None,
        )

        if with_blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(
                mot,
                scaled_model,
                os.path.join(output, "bodykin.csv"),
            )

        return output, mot, scaled_model

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
        if mode == "opensim":
            return self._visualize_opensim(motion_file, **kwargs)
        raise ValueError(
            f"Unsupported visualization mode '{mode}'. Use one of {supported_modes}",
        )

    def __str__(self):
        return f"Experiment(name={self.name}, path={self.path})"
