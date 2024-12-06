import contextlib

from TracX.tasks import EstimateMotionTask, KinematicsTask
from TracX.ui.common import BaseTaskButton
try:
    from TracX.rendering import render
except ImportError:
    def render(*args, **kwargs):
        raise ImportError(
            "The rendering module is not available. Please install the `requirements-extra.txt` file."
        )


class EstimateMotionButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__(None, EstimateMotionTask, None, callback)
        self.setText("Process")

    def on_start(self):
        super().on_start()
        self.setText("Processing...")

    def on_finish(self, status, result):
        super().on_finish(status, result)
        self.setText("Process")


class KinematicsButton(BaseTaskButton):
    def __init__(self, callback):
        super().__init__("visualize.png",  KinematicsTask, None, callback)

    def on_finish(self, status, result):
        super().on_finish(status, result)
        if status and result is not None:
            # Render the OpenSim files
            _, motion_file, model_file = result
            with contextlib.suppress(Exception):
                render(
                    osim=model_file,
                    mot=motion_file,
                )
