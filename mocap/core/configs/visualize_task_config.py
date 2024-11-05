from .task_config import TaskConfig


class VisualizeTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    def __init__(self):
        super().__init__(
            experiment_name=None,
            visualization_mode="naive",
            visualization_args=dict(),
            # skeleton=motion_config.skeleton if motion_config is not None else None,
            # visualization_mode = "opensim",
            # visualization_args = dict(
            #     with_blender=False,
            # ),
        )
