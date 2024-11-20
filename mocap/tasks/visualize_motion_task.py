import logging

from mocap.core import Experiment

from .base_task import BaseTask


class VisualizeMotionTask(BaseTask):
    """Task for visualizing estimated motion."""

    def __init__(self, config):
        super().__init__(config)

    def _execute_impl(self):
        # Read task configuration
        experiment_name = self.config

        if experiment_name is None:
            raise ValueError("Experiment name is required for visualization")

        logging.info("Visualizing 3D motion...")
        experiment = Experiment(experiment_name, create=False)
        result = experiment.visualize(
            mode="naive",
        )

        logging.info("Pipeline execution complete.")
        return result
