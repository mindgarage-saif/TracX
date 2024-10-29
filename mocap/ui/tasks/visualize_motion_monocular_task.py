from mocap.core import ExperimentMonocular

from .base_task import BaseTask, TaskConfig


class VisualizeMonocularTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    def __init__(self):
        super().__init__(
            experiment_name=None,
            visualization_mode="naive",
            visualization_args=dict(),
            # visualization_mode = "opensim",
            # visualization_args = dict(
            #     with_blender=False,
            # ),
        )


class VisualizeMotionMonocularTask(BaseTask):
    """Task for visualizing estimated motion."""

    def __init__(self, config: VisualizeMonocularTaskConfig):
        super().__init__(config)

    def execute(self):
        # Read task configuration
        experiment_name = self.config.experiment_name
        visualization_mode = self.config.visualization_mode
        visualization_args = self.config.visualization_args

        if experiment_name is None:
            return None

        print("Visualizing 3D motion...")
        experiment = ExperimentMonocular(experiment_name, create=False)
        result = experiment.visualize(
            mode=visualization_mode,
            **visualization_args,
        )

        print("Pipeline execution complete.")
        return result