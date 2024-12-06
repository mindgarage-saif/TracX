import logging
import os
import shutil
from typing import Optional

import toml
from easydict import EasyDict as edict

from Pose2Sim import Pose2Sim
from TracX.constants import (
    APP_ASSETS,
    APP_PROJECTS,
    SUPPORTED_VIDEO_FORMATS,
    FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED,
    FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED,
)

from .pose import PoseTracker2D, lift_to_3d
from .rotation import rotate_videos, unrotate_pose2d


class Experiment:
    def __init__(
        self,
        name,
        create=False,
        monocular=False,
        is_2d=False,
        base_dir=APP_PROJECTS,
    ) -> None:
        self.name = name
        self.path = os.path.abspath(os.path.join(base_dir, name))
        self.config_file = os.path.join(self.path, "Config.toml")
        self.videos_dir = os.path.join(self.path, "videos")
        self.pose2d_dir = os.path.join(self.path, "pose")
        self.pose2d_associated_dir = os.path.join(self.path, "pose-associated")
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
                self.is_2d = is_2d

                # Create the project directories.
                self._makedirs()

                # Read the configuration file.
                self.cfg = toml.load(self.config_file)
                self.cfg = edict(self.cfg)
            except Exception:
                raise ValueError(f"Experiment with name '{name}' already exists.")
        else:
            if not os.path.exists(self.path) or not os.path.exists(self.config_file):
                raise FileNotFoundError(f"No experiment with name '{name}' found.")

            # Read the configuration file.
            self.cfg = toml.load(self.config_file)
            self.cfg = edict(self.cfg)

            project_type = self.cfg.get("project", {}).get("type", "").lower()
            self.monocular = "mono" in project_type
            self.is_2d = "2d" in project_type

            # Set the project directories
            self._makedirs(exist_ok=True)

    @staticmethod
    def list():
        experiments = []
        for f in sorted(os.listdir(APP_PROJECTS)):
            if not os.path.isdir(os.path.join(APP_PROJECTS, f)):
                continue

            # Open the experiment and read the metadata
            e = Experiment.open(f)

            # Skip experiments that are not enabled
            if e.is_2d and not FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED:
                continue

            if e.monocular and not FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED:
                continue

            experiments.append(
                {
                    "name": f,
                    "monocular": e.monocular,
                    "is_2d": e.is_2d,
                    "path": os.path.join(APP_PROJECTS, f),
                }
            )

        return experiments

    @staticmethod
    def open(name):
        logging.debug(f"Opening experiment '{name}'...")
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

    def calibrate_cameras(
            self,
            overwrite_intrinsics=True,
            intrinsics_extension="jpg",
            intrinsics_corners_nb=(8, 13),
            intrinsics_square_size=20, # mm
            calculate_extrinsics=True,
            extrinsics_method="board",
            extrinsics_extension="jpg",
            extrinsics_corners_nb=(8, 13),
            extrinsics_square_size=20, # mm
            show_reprojection_error=True,
    ):
        # Update parameters in the configuration file
        cfg = self.cfg
        cfg.calibration.calibration_type = "calculate"

        # [calibration.calculate.intrinsics]
        cfg.calibration.calculate.intrinsics.overwrite_intrinsics = overwrite_intrinsics
        cfg.calibration.calculate.intrinsics.intrinsics_extension = intrinsics_extension
        cfg.calibration.calculate.intrinsics.intrinsics_corners_nb = intrinsics_corners_nb
        cfg.calibration.calculate.intrinsics.intrinsics_square_size = intrinsics_square_size

        # [calibration.calculate.extrinsics]
        cfg.calibration.calculate.extrinsics.calculate_extrinsics = calculate_extrinsics
        cfg.calibration.calculate.extrinsics.extrinsics_method = extrinsics_method
        cfg.calibration.calculate.extrinsics.board.extrinsics_extension = extrinsics_extension
        cfg.calibration.calculate.extrinsics.board.extrinsics_corners_nb = extrinsics_corners_nb
        cfg.calibration.calculate.extrinsics.board.extrinsics_square_size = extrinsics_square_size
        cfg.calibration.calculate.extrinsics.board.show_reprojection_error = show_reprojection_error

        # Update the configuration file
        self.update_config(cfg)

        # Execute the calibration
        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            Pose2Sim.calibration()
        except Exception as e:
            logging.error(f"Failed to calibrate cameras: {e}")

            import traceback
            logging.debug(traceback.format_exc())
        finally:
            os.chdir(cwd)

    def calibrate_extrinsics(
        self,
        person_height=1.74, # meters
        extrinsics_extension="jpg",
    ):
        extrinsics_folder = os.path.join(self.calibration_dir, "extrinsics")

        def estimate_pose(image_path):
            pass

        poses = {}
        for cam in os.listdir(extrinsics_folder):
            cam_folder = os.path.join(extrinsics_folder, cam)
            if not os.path.isdir(cam_folder):
                continue

            # Get the first image in the camera folder
            img_files = [
                f for f in os.listdir(cam_folder) if f.endswith(extrinsics_extension)
            ]
            if len(img_files) == 0:
                raise ValueError(f"No images found for camera '{cam}'")
            
            # NOTE: This must be a T-pose image showing the full body!!!
            #       which should be automatically verified and an error
            #       should be raised if the image is not valid.
            # TODO: Implement the image validation
            img_file = os.path.join(cam_folder, img_files[0])

            # Estimate the pose from the image
            poses[cam] = estimate_pose(img_file)

        # Define a set of 3D points for the person
        points = [
            (0, 0, 0),  # Origin at middle of heels
            (0, 0, person_height),  # Z-axis pointing upwards (using head top)
        ]

        # Set the middle of heels as the origin
        L_HEEL_IDX = 24
        R_HEEL_IDX = 25
        heel_mid = (poses["cam1"][L_HEEL_IDX] + poses["cam2"][R_HEEL_IDX]) / 2
        pass

    def set_camera_parameters(self, params_file):
        if params_file.split(".")[-1].lower() != "toml":
            raise ValueError(
                "Invalid calibration file format. We except a calibration file in toml format.",
            )

        shutil.copy(params_file, self.calibration_file)

    def get_camera_parameters(self):
        all_files = os.listdir(self.calibration_dir)
        for file in all_files:
            if file.startswith("Calib_") and file.endswith(".toml"):
                self.calibration_file = os.path.join(self.calibration_dir, file)
                return os.path.join(self.calibration_dir, file)

        return None

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

    def process(self):
        # Change the working directory to the project directory.
        cwd = os.getcwd()
        os.chdir(self.path)

        # Update the configuration file with selected settings
        if not self.has_videos():
            raise ValueError("No videos found in the project directory.")

        cfg = self.cfg
        correct_rotation = cfg.get("pose").get("correct_camera_rotation", False)
        if correct_rotation and not self.monocular:
            calibration_file = os.path.join(
                self.calibration_dir, "camera_parameters.qca.txt"
            )
            rotated_dir = os.path.join(self.path, self.videos_dir + "_rotated")
            if not os.path.exists(rotated_dir):
                rotate_videos(self.videos, rotated_dir, calibration_file)
            else:
                logging.info("Rotated videos already exist. Skipping rotation...")

            # Rename the videos directories to use the rotated videos
            if os.path.exists(self.videos_dir) and os.path.exists(rotated_dir):
                os.rename(self.videos_dir, self.videos_dir + "_original")
                os.rename(rotated_dir, self.videos_dir)

        # Set video format and overwrite flag
        # TODO: Read these from self.cfg
        videos_format = os.path.splitext(self.videos[0])[-1].lower()
        overwrite = cfg.get("pose").get("overwrite_pose", False)

        # Execute the 2D pose estimation
        logging.info("Executing 2D pose estimatioan...")
        res_w, res_h = 0, 0
        # TODO: Do not hardcode the model names here
        if cfg.pose.pose_model in ["COCO_17", "COCO_133", "HALPE_26", "BODY_43", "WHOLEBODY_150"]:
            Pose2Sim.poseEstimation()
        elif cfg.pose.pose_model == "BODY_43":
            res_w, res_h, _ = PoseTracker2D.estimateBodyWithSpine(
                videos=self.videos_dir,
                save_dir=self.pose2d_dir,
                video_format=videos_format,
                overwrite=overwrite,
            )
        else:
            raise ValueError(f"Unsupported custom pose model '{cfg.pose.pose_model}'")

        # Unrotate the 2D poses
        if correct_rotation:
            # Restore the original videos
            os.rename(self.videos_dir, self.videos_dir + "_rotated")
            os.rename(self.videos_dir + "_original", self.videos_dir)

            logging.info("Rotating 2D poses back...")
            unrotate_pose2d(self.pose2d_dir, calibration_file)

        # Person association
        logging.info("Finding the most prominent person...")
        Pose2Sim.personAssociation()

        # 2D-to-3D Lifting in Monocular Mode
        if self.monocular:
            # TODO: Update this to output a .trc file
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
            # TODO: Wrap triangulation in a try-except block and throw a nice error message
            logging.info("Triangulating 3D poses...")
            Pose2Sim.triangulation()

        # Filtering
        logging.info("Smoothing triangulated poses...")
        Pose2Sim.filtering()

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
        return self.cfg.get("pose", {}).get("pose_model", "HALPE_26")

    def __str__(self):
        return f"Experiment(name={self.name}, path={self.path})"
