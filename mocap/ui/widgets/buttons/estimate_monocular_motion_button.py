from mocap.ui.tasks import EstimateMotionMonocularTask

from .task_button import BaseTaskButton


class EstimateMonocularMotionButton(BaseTaskButton):
    def __init__(self, task_config, callback):
        super().__init__("Estimate Monocular Motion", EstimateMotionMonocularTask, task_config, callback)

    def on_start(self):
        super().on_start()
        self.setText("Processing...")

    def on_finish(self, status, result):
        super().on_finish(status, result)
        self.setText("Estimate Motion Monocular")
        if status:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
