import json
import logging

from mocap.core import Experiment

from .base_task import BaseTask, TaskConfig


class MotionTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    SUPPORTED_MODES = ["multiview", "monocular"]
    SUPPORTED_ENGINES = ["Pose2Sim", "Custom"]
    SUPPORTED_POSE2SIM_MODELS = ["COCO_17", "COCO_133", "HALPE_26"]
    SUPPORTED_POSE2SIM_MODES = ["lightweight", "balanced", "performance"]
    SUPPORTED_CUSTOM_MONOCULAR_MODELS = ["Baseline", "MotionBERT"]
    SUPPORTED_CUSTOM_MULTIVIEW_MODELS = ["DFKI_Body43", "DFKI_Spine17"]

    def __init__(self):
        super().__init__(
            experiment_name=None,
            mode="multiview",
            engine="Pose2Sim",
            pose2d_model="HALPE_26",
            pose2d_kwargs=dict(mode="lightweight"),
            lifting_model="Baseline",
            lifting_kwargs=dict(),
            trackedpoint="Neck",
            correct_rotation=False,
            use_marker_augmentation=False,
        )

        if self.mode == "monocular":
            self.engine = "Custom"
            self.pose2d_model = "HALPE_26"
            self.pose2d_kwargs = dict(mode="lightweight")

    def validate(self):
        """Validates the configuration."""
        logging.debug(f"Validating motion task configuration: {self}")
        if self.mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Invalid mode: {self.mode}")

        if self.engine not in self.SUPPORTED_ENGINES:
            raise ValueError(f"Invalid engine: {self.engine}")

        if self.mode == "monocular" and self.engine != "Custom":
            raise ValueError("Monocular mode only supports custom engine")

        if self.engine == "Pose2Sim":
            if self.pose2d_model not in self.SUPPORTED_POSE2SIM_MODELS:
                raise ValueError(f"Invalid Pose2Sim model: {self.pose2d_model}")
            if self.pose2d_kwargs["mode"] not in self.SUPPORTED_POSE2SIM_MODES:
                raise ValueError(f"Invalid Pose2Sim mode: {self.pose2d_kwargs['mode']}")

        if self.engine == "Custom":
            if (
                self.mode == "multiview"
                and self.pose2d_model not in self.SUPPORTED_CUSTOM_MULTIVIEW_MODELS
            ):
                raise ValueError(f"Invalid multiview model: {self.lifting_model}")
            if (
                self.mode == "monocular"
                and self.lifting_model not in self.SUPPORTED_CUSTOM_MONOCULAR_MODELS
            ):
                raise ValueError(f"Invalid monocular model: {self.lifting_model}")

        logging.debug("Configuration is valid")
        return True


class EstimateMotionTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, config: MotionTaskConfig):
        super().__init__(config)

    def _execute_impl(self):
        # Read parameters
        cfg = self.config.copy()
        experiment_name = cfg.pop("experiment_name")
        logging.info(
            f"Preparing experiment '{experiment_name}' for motion estimation..."
        )

        # Initialize experiment
        experiment = Experiment(experiment_name, create=False)
        logging.info("Experiment configuration:")
        logging.info(f"{json.dumps(experiment.cfg)}")
        logging.debug(f"Experiment has {experiment.num_videos} video(s)")

        # Estimate motion
        logging.info("Starting motion estimation...")
        logging.debug(f"Parameters: {cfg}")
        experiment.process(**self.config)

        logging.info("Motion estimation completed successfully")
