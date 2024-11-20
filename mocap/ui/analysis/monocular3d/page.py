import logging
import os

import numpy as np
import onnxruntime as ort
from PyQt6.QtWidgets import (
    QWidget,
)

from mocap.constants import APP_ASSETS
from mocap.core.analyze2d import process_frame

from ..monocular2d.page import Monocular2DAnalysisPage


def normalize_data(data, res_w, res_h):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def lift_to_3d(model, keypoints, res_w, res_h):
    data_2d = np.array(
        keypoints[[19, 12, 14, 16, 11, 13, 15, 18, 0, 17, 5, 7, 9, 6, 8, 10], :2],
        dtype=np.float32,
    )
    input2 = normalize_data(data_2d, res_w, res_h)
    input2 = input2.reshape(1, -1)
    onnx_input = {"l_x_": input2}

    output = model.run(None, onnx_input)
    return output[0][0].reshape(16, 3)


class Monocular3DAnalysisPage(Monocular2DAnalysisPage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.settings.title_label.setText("Monocular 3D Analysis")
        self._lifting_model = None

    @property
    def lifting_model(self):
        if self._lifting_model is not None:
            return self._lifting_model

        # Load lifting model
        model_path = os.path.join(APP_ASSETS, "models", "lifting", "baseline.onnx")
        logging.info("Loading the 3D lifting model from %s...", model_path)
        self._lifting_model = ort.InferenceSession(model_path)
        logging.info("3D lifting model loaded successfully.")

        # Log model inputs and outputs for debugging
        logging.debug("3D lifting model inputs:")
        for input in self._lifting_model.get_inputs():
            logging.debug(
                "  Name: %s, Shape: %s, Type: %s", input.name, input.shape, input.type
            )
        logging.debug("3D lifting model outputs:")
        for output in self._lifting_model.get_outputs():
            logging.debug(
                "  Name: %s, Shape: %s, Type: %s",
                output.name,
                output.shape,
                output.type,
            )

        return self._lifting_model

    def processFrame(self, frame):
        if self.model is None:
            return frame

        logging.debug("Estimating 2D pose")
        frame, (x, y, scores, angles, kwargs) = process_frame(
            self.experiment.cfg, self.model, frame
        )

        # Append frame data
        self.all_frames_X.append(np.array(x))
        self.all_frames_Y.append(np.array(y))
        self.all_frames_scores.append(np.array(scores))
        self.all_frames_angles.append(np.array(angles))
        self.postprocessing_kwargs = kwargs

        # TODO: Lift to 3D
        logging.debug("Lifting to 3D")
        height, width = frame.shape[:2]
        pose2d = np.array([np.array(x)[0, :], np.array(y)[0, :]]).T
        logging.debug("Pose2D: %s", pose2d.shape)
        pose3d = lift_to_3d(self.lifting_model, pose2d, width, height)
        logging.debug("Pose3D: %s", pose3d.shape)

        # TODO: Compute angles
        logging.debug("Computing angles")

        return frame
