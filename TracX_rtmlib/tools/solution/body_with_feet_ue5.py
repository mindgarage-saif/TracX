import os

import numpy as np
from rtmlib import YOLOX, RTMPose

# FIXME: This import should not be here. Upload model somewhere online and add a link
from TracX.constants import APP_ASSETS


import numpy as np


class BodyWithFeetUE5:
    """
    BodyWithFeetUE5 class for human pose estimation using the DFKI_Body53 keypoint format
    which extends HALPE_26 with additional 27 points from the Unreal Engine 5 Mannequin.
    """

    MODE = {
        "performance": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip",
            "det_input_size": (640, 640),
            "pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body43",
                "rtmpose-l_body53-256x192.onnx",
            ),
            "pose_input_size": (192, 256),
        },
        "lightweight": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_tiny_8xb8-300e_humanart-6f3252f9.zip",
            "det_input_size": (416, 416),
            "pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body53",
                "rtmpose-l_body53-256x192.onnx",
            ),
            "pose_input_size": (192, 256),
        },
        "balanced": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_m_8xb8-300e_humanart-c2c7a14a.zip",
            "det_input_size": (640, 640),
            "pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body53",
                "rtmpose-l_body53-256x192.onnx",
            ),
            "pose_input_size": (192, 256),
        },
    }

    def __init__(
        self,
        mode: str = "performance",
        to_openpose: bool = False,
        backend="onnxruntime",
        device: str = "cpu",
    ):
        """
        Initialize the DFKI_Body53 pose estimation model.

        Args:
            mode (str, optional): Operation mode ('performance', 'lightweight', or 'balanced'). Default is 'performance'.
            to_openpose (bool, optional): Whether to convert output to OpenPose format. Default is False.
            backend (str, optional): Backend for inference ('onnxruntime' or 'opencv'). Default is 'onnxruntime'.
            device (str, optional): Device for inference ('cpu' or 'cuda'). Default is 'cpu'.
        """

        pose = self.MODE[mode]["pose"]
        pose_input_size = self.MODE[mode]["pose_input_size"]

        det = self.MODE[mode]["det"]
        det_input_size = self.MODE[mode]["det_input_size"]

        self.det_model = YOLOX(
            det, model_input_size=det_input_size, backend=backend, device=device
        )
        self.body_model = RTMPose(
            pose,
            model_input_size=pose_input_size,
            to_openpose=to_openpose,
            backend=backend,
            device=device,
        )
        self.pose_model = RTMPose(
            self.MODE[mode]["pose"],
            model_input_size=self.MODE[mode]["pose_input_size"],
            to_openpose=to_openpose,
            backend=backend,
            device=device,
        )

    def __call__(self, image: np.ndarray):
        """
        Perform pose estimation on the input image.

        Args:
            image (np.ndarray): Input image for pose estimation.

        Returns:
            tuple: A tuple containing:
                - keypoints (np.ndarray): Estimated keypoint coordinates.
                - scores (np.ndarray): Confidence scores for each keypoint.
        """
        bboxes = self.det_model(image)
        keypoints, scores = self.pose_model(image, bboxes=bboxes)
        return keypoints, scores
