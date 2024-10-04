import os

# Define application metadata.
APP_NAME = "PoseTrack Studio"
APP_NAME_SLUG = APP_NAME.lower().replace(" ", "-")
APP_VERSION = "0.1.0"

# Define paths.
APP_HOME = os.path.dirname(os.path.abspath(__file__))
APP_ASSETS = os.path.join(APP_HOME, "..", "assets")
APP_CACHE = os.path.join(os.path.expanduser("~"), ".cache", APP_NAME_SLUG)
APP_FILES = os.path.join(os.path.expanduser("~"), APP_NAME)
APP_RECORDINGS = os.path.join(APP_FILES, "Recordings")
APP_PROJECTS = os.path.join(APP_FILES, "Projects")

OPENSIM_DIR = os.path.join(APP_ASSETS, "opensim", "Pose2Sim_Halpe26")

# Define supported formats.
SUPPORTED_VIDEO_FORMATS = ["mp4", "avi"]
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png"]


def create_directories():
    """Create necessary directories."""
    for directory in [APP_CACHE, APP_FILES, APP_RECORDINGS, APP_PROJECTS]:
        os.makedirs(directory, exist_ok=True)
