import os

# Define application metadata.
APP_NAME = "TracX"
APP_NAME_SLUG = APP_NAME.lower().replace(" ", "-")
APP_VERSION = "0.1.0"

# Define paths.
APP_HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
APP_ASSETS = os.path.join(APP_HOME, "assets")
APP_CACHE = os.path.join(os.path.expanduser("~"), ".cache", APP_NAME_SLUG)
APP_FILES = os.path.join(os.path.expanduser("~"), APP_NAME)
APP_RECORDINGS = os.path.join(APP_FILES, "Recordings")
APP_PROJECTS = os.path.join(APP_FILES, "Projects")

POSE2SIM_ASSETS = os.path.join(APP_HOME, "Pose2Sim", "OpenSim_Setup")
OPENSIM_GEOMETRY = os.path.join(POSE2SIM_ASSETS, "Geometry")
OPENSIM_FILES = {
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
    }
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
