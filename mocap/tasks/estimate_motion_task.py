import json
import logging

from mocap.core import Experiment
from mocap.core.configs import MotionTaskConfig

from .base_task import BaseTask


class EstimateMotionTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, config):
        super().__init__(config)

    def _execute_impl(self):
        # Read parameters
        cfg: MotionTaskConfig = self.config.copy()
        experiment_name = cfg.pop("experiment_name", None)
        if not experiment_name:
            raise ValueError("Experiment name must be provided")

        # Initialize experiment
        logging.info(f"Preparing experiment '{experiment_name}'...")
        experiment = Experiment.open(experiment_name)

        # Log debug information
        logging.debug(f"{json.dumps(experiment.cfg)}")
        logging.debug(f"Found {experiment.num_videos} video(s)")
        logging.debug(f"Parameters: {cfg}")

        # Estimate motion
        logging.info("Estimating motion...")
        experiment.process(cfg)
