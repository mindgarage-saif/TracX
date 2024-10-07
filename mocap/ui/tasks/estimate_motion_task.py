import json

from mocap.core import Experiment

from .base_task import BaseTask, TaskConfig


class MotionTaskConfig(TaskConfig):
    """
    Configuration class for motion estimation tasks.
    """

    def __init__(self):
        super().__init__(
            experiment_name=None,
            correct_rotation=False,
            use_marker_augmentation=False,
        )


class EstimateMotionTask(BaseTask):
    """
    Task for estimating motion.
    """

    def __init__(self, config: MotionTaskConfig):
        super().__init__(config)

    def _execute_impl(self):
        # Read task configuration
        experiment_name = self.config.experiment_name
        correct_rotation = self.config.correct_rotation
        use_marker_augmentation = self.config.use_marker_augmentation

        # Initialize the experiment
        print("Loading experiment...")
        experiment = Experiment(experiment_name, create=False)
        print(
            f"'{experiment.name}' has {experiment.num_videos} video(s) with configuration:"
        )
        print(f"{json.dumps(experiment.cfg, indent=2)}")

        print("Estimating motion...")
        experiment.process(
            correct_rotation=correct_rotation,
            use_marker_augmentation=use_marker_augmentation,
        )

        print("Motion estimation complete")
