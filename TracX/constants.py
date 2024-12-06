import os

# Define application metadata.
APP_NAME = "TracX"
APP_NAME_SLUG = APP_NAME.lower().replace(" ", "-")
APP_VERSION = "0.1.0"

# Define paths.
APP_HOME = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
APP_ASSETS = os.path.join(APP_HOME, "assets")
APP_CACHE = os.path.join(os.path.expanduser("~"), ".cache", APP_NAME_SLUG)
APP_FILES = os.path.join(os.path.expanduser("~"), APP_NAME)
APP_RECORDINGS = os.path.join(APP_FILES, "Recordings")
APP_PROJECTS = os.path.join(APP_FILES, "Projects")

POSE2SIM_ASSETS = os.path.join(APP_HOME, "Pose2Sim", "OpenSim_Setup")
OPENSIM_GEOMETRY = os.path.join(POSE2SIM_ASSETS, "Geometry")
OPENSIM_FILES = {
    "BODY_43": {
        "Model": os.path.join(APP_ASSETS, "models", "3D", "Model_DFKI_Body43.osim"),
        "Scaling_Setup": os.path.join(APP_ASSETS, "models", "3D", "Scaling_Setup_DFKI_Body43.xml"),
        "IK_Setup": os.path.join(APP_ASSETS, "models", "3D", "IK_Setup_DFKI_Body43.xml"),
    },
    "COCO_17": {
        "Model": os.path.join(POSE2SIM_ASSETS, "Model_Pose2Sim_Coco17.osim"),
        "Scaling_Setup": os.path.join(POSE2SIM_ASSETS, "Scaling_Setup_Pose2Sim_Coco17.xml"),
        "IK_Setup": os.path.join(POSE2SIM_ASSETS, "IK_Setup_Pose2Sim_Coco17.xml"),
    },
    "COCO_133": {
        "Model": os.path.join(POSE2SIM_ASSETS, "Model_Pose2Sim_Coco133.osim"),
        "Scaling_Setup": os.path.join(POSE2SIM_ASSETS, "Scaling_Setup_Pose2Sim_Coco133.xml"),
        "IK_Setup": os.path.join(POSE2SIM_ASSETS, "IK_Setup_Pose2Sim_Coco133.xml"),
    },
    "HALPE_26": {
        "Model": os.path.join(POSE2SIM_ASSETS, "Model_Pose2Sim_Halpe26.osim"),
        "Scaling_Setup": os.path.join(POSE2SIM_ASSETS, "Scaling_Setup_Pose2Sim_Halpe26.xml"),
        "IK_Setup": os.path.join(POSE2SIM_ASSETS, "IK_Setup_Pose2Sim_Halpe26.xml"),
    },
    "WHOLEBODY_150": {  # TODO: Reusing COCO_133 files for now until new files are available.
        "Model": os.path.join(POSE2SIM_ASSETS, "Model_Pose2Sim_Coco133.osim"),
        "Scaling_Setup": os.path.join(POSE2SIM_ASSETS, "Scaling_Setup_Pose2Sim_Coco133.xml"),
        "IK_Setup": os.path.join(POSE2SIM_ASSETS, "IK_Setup_Pose2Sim_Coco133.xml"),
    },
    # TODO: Add OpenSim files for hands and face models.
}

# Define supported formats.
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov"]
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png"]

# Other constants.
MIN_VIDEOS = 1
MAX_VIDEOS = 15


def create_directories():
    """Create necessary directories."""
    for directory in [APP_CACHE, APP_FILES, APP_RECORDINGS, APP_PROJECTS]:
        os.makedirs(directory, exist_ok=True)


# Enable feature flags (set using environment variables).
FEATURE_RECORDING_ENABLED = os.getenv("FEATURE_RECORDING_ENABLED", "0") == "1"
FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED = os.getenv("FEATURE_MONOCULAR_2D_ANALYSIS_ENABLED", "0") == "1"
FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED = os.getenv("FEATURE_MONOCULAR_3D_ANALYSIS_ENABLED", "0") == "1"
FEATURE_STREAMING_ENABLED = os.getenv("FEATURE_STREAMING_ENABLED", "0") == "1"