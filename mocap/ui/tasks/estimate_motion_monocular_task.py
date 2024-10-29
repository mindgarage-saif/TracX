import json

from mocap.core import ExperimentMonocular

from .base_task import BaseTask, TaskConfig


class MonocularMotionTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    def __init__(self):
        super().__init__(
            rotation=90,
            experiment_name=None,
            correct_rotation=False,
            model="lightweight",
        )


class EstimateMotionMonocularTask(BaseTask):
    """Task for estimating motion."""

    def __init__(self, config: MonocularMotionTaskConfig):
        super().__init__(config)

    def _execute_impl(self):
        # Read task configuration
        experiment_name = self.config.experiment_name
        correct_rotation = self.config.correct_rotation
        rotation = self.config.rotation
        # Initialize the experiment
        print("Loading experiment...")
        experiment = ExperimentMonocular(experiment_name, create=False)
        print(
            f"'{experiment.name}' has {experiment.num_videos} video(s) with configuration:",
        )
        print(f"{json.dumps(experiment.cfg, indent=2)}")

        print("Estimating motion...")
        experiment.process_monocular(
            mode=self.config.model,
            correct_rotation=correct_rotation,
            rotation=rotation,
        )

        print("Motion estimation complete")
