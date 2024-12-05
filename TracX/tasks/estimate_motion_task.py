from TracX import TracX

from .base_task import BaseTask


class EstimateMotionTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, experiment):
        super().__init__(experiment)

    def _execute_impl(self):
        # Read parameters
        experiment_name = self.experiment
        if not experiment_name:
            raise ValueError("Experiment name is required")

        TracX.process(experiment_name)

        # TODO: Investigate why kinematics processing is blocking the UI
        TracX.kinematics(self.experiment, overwrite=True)
