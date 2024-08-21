from PyQt5.QtCore import QObject, pyqtSignal


class RuntimeParams(QObject):
    fpsUpdated = pyqtSignal(float)
    inferenceSpeedUpdated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._fps = 0.0
        self._inferenceSpeed = 0.0

    def set_fps(self, fps):
        if fps != self._fps:
            self._fps = fps
            self.fpsUpdated.emit(self._fps)

    def set_inference_speed(self, speed):
        if speed != self._inferenceSpeed:
            self._inferenceSpeed = speed
            self.inferenceSpeedUpdated.emit(self._inferenceSpeed)
