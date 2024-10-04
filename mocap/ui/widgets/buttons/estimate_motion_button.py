from PyQt6.QtWidgets import QPushButton, QWidget

from mocap.core.pipeline import execute_pipeline


class EstimateMotionButton(QPushButton):
    def __init__(self, parent: QWidget, params) -> None:
        super().__init__("Estimate Motion", parent)
        self.params = params
        self.clicked.connect(self.execute)

    def execute(self):
        execute_pipeline(**self.params)
