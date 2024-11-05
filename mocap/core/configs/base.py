from enum import Enum


## 2D Pose Estimation Configurations
class Engine(Enum):
    """Enum for the different backend engines.

    Attributes:
        POSE2SIM: Pose2Sim with built-in models is used for 2D pose estimation.
        RTMLIB: RTMLib with custom models is used for 2D pose estimation.
    """

    POSE2SIM = 1
    RTMLIB = 2


class PoseModel(Enum):
    """Enum for the different 2D pose estimation models."""

    COCO_17 = 1
    COCO_133 = 2
    HALPE_26 = 3
    DFKI_BODY43 = 4
    DFKI_SPINE17 = 5


class PoseModelCompatibilityMatrix:
    """Compatibility matrix for engine-model combinations."""

    MATRIX = {
        Engine.POSE2SIM: [PoseModel.COCO_17, PoseModel.COCO_133, PoseModel.HALPE_26],
        Engine.RTMLIB: [
            PoseModel.HALPE_26,
            PoseModel.DFKI_BODY43,
            PoseModel.DFKI_SPINE17,
        ],
    }

    @classmethod
    def is_compatible(cls, engine, model):
        """Check if the engine-model combination is compatible."""
        return model in cls.MATRIX[engine]


## 3D Pose Lifting Configurations
class ExperimentMode(Enum):
    """Enum for the different experiment modes.

    Attributes:
        MONOCULAR: Monocular mode (single-view to 2D pose followed by lifting).
        MULTIVIEW: Multiview mode (multi-views to 2D poses followed by triangulation).
    """

    MONOCULAR = 1
    MULTIVIEW = 2


class LiftingModel(Enum):
    """Enum for the different 3D pose lifting models."""

    BASELINE = 1
    MOTIONBERT = 2


class LiftingModelCompatibilityMatrix:
    """Compatibility matrix for engine-lifting model combinations."""

    MATRIX = {
        Engine.POSE2SIM: [LiftingModel.BASELINE, LiftingModel.MOTIONBERT],
        Engine.RTMLIB: [],
    }

    @classmethod
    def is_compatible(cls, engine, model):
        """Check if the engine-model combination is compatible."""
        return model in cls.MATRIX[engine]
