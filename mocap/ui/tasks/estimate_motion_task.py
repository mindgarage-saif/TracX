import json
import os

import toml

from mocap.constants import APP_PROJECTS
from mocap.core import Experiment

from .base_task import BaseTask, TaskConfig


class MotionTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    def __init__(self):
        super().__init__(
            experiment_name=None,
            correct_rotation=False,
            use_marker_augmentation=False,
            mode="lightweight",
            skeleton="HALPE_26",
            trackedpoint="Neck",
            rotation=90,
        )


class EstimateMotionTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, config: MotionTaskConfig):
        super().__init__(config)

    def _execute_impl(self):
        # Read task configuration
        experiment_name = self.config.experiment_name
        correct_rotation = self.config.correct_rotation
        use_marker_augmentation = self.config.use_marker_augmentation
        rotation = self.config.rotation
        self.path = os.path.abspath(os.path.join(APP_PROJECTS, experiment_name))
        config_path = os.path.join(self.path, "Config.toml")
        mode = self.config.mode
        skeleton = self.config.skeleton
        trackedpoint = self.config.trackedpoint
        self.change_config(config_path, mode, skeleton, trackedpoint=trackedpoint)
        custom_model = skeleton == "CUSTOM"
        # Initialize the experiment
        print("Loading experiment...")
        experiment = Experiment(experiment_name, create=False)
        print(
            f"'{experiment.name}' has {experiment.num_videos} video(s) with configuration:",
        )
        print(f"{json.dumps(experiment.cfg, indent=2)}")

        print("Estimating motion...")
        experiment.process(
            correct_rotation=correct_rotation,
            use_marker_augmentation=use_marker_augmentation,
            custom_model=custom_model,
            mode=self.config.model,
            rotation=rotation,
        )

        print("Motion estimation complete")

    def change_config(self, path, mode, skeleton, trackedpoint):
        file = toml.load(path)
        file["pose"]["pose_model"] = skeleton
        file["pose"]["mode"] = mode
        file["personAssociation"]["single_person"]["tracked_keypoint"] = trackedpoint
        with open(path, "w") as f:
            toml.dump(file, f)
