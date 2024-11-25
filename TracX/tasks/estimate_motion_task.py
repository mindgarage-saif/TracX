from TracX import TracX

from .base_task import BaseTask


class EstimateMotionTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, config):
        super().__init__(config)

    def _execute_impl(self):
        # Read parameters
        experiment_name = self.experiment
        if not experiment_name:
            raise ValueError("Experiment name must be provided")

        TracX.process(experiment_name)
