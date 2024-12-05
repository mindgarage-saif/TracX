from TracX import TracX

from .base_task import BaseTask


class KinematicsTask(BaseTask):
    """Task for performing kinematics analysis."""

    def __init__(self, experiment):
        super().__init__(experiment)

    def _execute_impl(self):
        # Read parameters
        experiment_name = self.experiment
        if not experiment_name:
            raise ValueError("Experiment name is required")

        return TracX.kinematics(self.experiment)
