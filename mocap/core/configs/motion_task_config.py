from .base import (
    Engine,
    ExperimentMode,
    LiftingModel,
    LiftingModelCompatibilityMatrix,
    PoseModel,
    PoseModelCompatibilityMatrix,
)
from .task_config import TaskConfig


class MotionTaskConfig(TaskConfig):
    """Configuration class for motion estimation tasks."""

    def __init__(self):
        super().__init__(
            experiment_name=None,
            mode=ExperimentMode.MULTIVIEW,
            engine=Engine.POSE2SIM,
            pose2d_model=PoseModel.HALPE_26,
            pose2d_kwargs=dict(mode="lightweight"),
            lifting_model=LiftingModel.BASELINE,
            lifting_kwargs=dict(),
            trackedpoint="Neck",
            correct_rotation=False,
            use_marker_augmentation=False,
            multi_person=False,
        )

        # Check compatibility.
        if not PoseModelCompatibilityMatrix.is_compatible(
            self.engine, self.pose2d_model
        ):
            raise ValueError(
                f"Pose2D model '{self.pose2d_model}' is not compatible with engine '{self.engine}'"
            )
        if (
            self.mode == ExperimentMode.MONOCULAR
            and not LiftingModelCompatibilityMatrix.is_compatible(
                self.engine, self.lifting_model
            )
        ):
            raise ValueError(
                f"Lifting model '{self.lifting_model}' is not compatible with engine '{self.engine}'"
            )

    def validate(self):
        """Validates the configuration."""
        return True
