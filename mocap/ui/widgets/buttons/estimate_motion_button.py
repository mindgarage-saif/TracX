from mocap.ui.tasks import EstimateMotionTask

from .task_button import BaseTaskButton


class EstimateMotionButton(BaseTaskButton):
    def __init__(self, task_config, callback):
        super().__init__("Estimate Motion", EstimateMotionTask, task_config, callback)

    def on_start(self):
        super().on_start()
        self.setText("Processing...")

    def on_finished(self, status, result):
        super().on_finished(status, result)
        self.setText("Estimate Motion")
        if status:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
