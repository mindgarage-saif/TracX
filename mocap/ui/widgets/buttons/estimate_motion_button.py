import threading

from PyQt6.QtWidgets import QPushButton, QWidget

from mocap.core.pipeline import execute_pipeline


def run_in_thread(target_function, *args, **kwargs):
    thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
    thread.start()


class EstimateMotionButton(QPushButton):
    def __init__(self, parent: QWidget, params) -> None:
        super().__init__("Estimate Motion", parent)
        self.params = params
        self.clicked.connect(self.execute)

    def execute(self):
        run_in_thread(execute_pipeline, **self.params)
