import os

import numpy as np
from rtmlib import YOLOX, RTMPose

# FIXME: This import should not be here. Upload model somewhere online and add a link
from TracX.constants import APP_ASSETS


class WholebodyWithSpine:
    MODE = {
        "performance": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_m_8xb8-300e_humanart-c2c7a14a.zip",  # noqa
            "det_input_size": (640, 640),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmw/onnx_sdk/rtmw-dw-x-l_simcc-cocktail14_270e-384x288_20231122.zip",  # noqa
            "pose_input_size": (288, 384),
            "spine_pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body43",
                "rtmpose-l_body43-384x288.onnx",
            ),
            "spine_pose_input_size": (288, 384),
        },
        "lightweight": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_tiny_8xb8-300e_humanart-6f3252f9.zip",  # noqa
            "det_input_size": (416, 416),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmw/onnx_sdk/rtmw-dw-l-m_simcc-cocktail14_270e-256x192_20231122.zip",  # noqa
            "pose_input_size": (192, 256),
            "spine_pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body43",
                "rtmpose-l_body43-384x288.onnx",
            ),
            "spine_pose_input_size": (288, 384),
        },
        "balanced": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_m_8xb8-300e_humanart-c2c7a14a.zip",  # noqa
            "det_input_size": (640, 640),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmw/onnx_sdk/rtmw-x_simcc-cocktail13_pt-ucoco_270e-256x192-fbef0d61_20230925.zip",  # noqa
            "pose_input_size": (192, 256),
            "spine_pose": os.path.join(
                APP_ASSETS,
                "models",
                "2D",
                "DFKI_Body43",
                "rtmpose-l_body43-384x288.onnx",
            ),
            "spine_pose_input_size": (288, 384),
        },
    }

    def __init__(
        self,
        det: str = None,
        det_input_size: tuple = (640, 640),
        pose: str = None,
        pose_input_size: tuple = (288, 384),
        mode: str = "balanced",
        to_openpose: bool = False,
        backend: str = "onnxruntime",
        device: str = "cpu",
    ):
        if det is None:
            det = self.MODE[mode]["det"]
            det_input_size = self.MODE[mode]["det_input_size"]

        if pose is None:
            pose = self.MODE[mode]["pose"]
            pose_input_size = self.MODE[mode]["pose_input_size"]

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
        self.spine_pose = RTMPose(
            self.MODE[mode]["spine_pose"],
            model_input_size=self.MODE[mode]["spine_pose_input_size"],
            to_openpose=to_openpose,
            backend=backend,
            device=device,
        )

        def forward(image, bboxes):
            keypoints, scores = self.body_model(image, bboxes=bboxes)
            spine_keypoints, spine_scores = self.spine_pose(image, bboxes=bboxes)
            spine_keypoints = spine_keypoints[:, -17:]
            spine_scores = spine_scores[:, -17:]
            keypoints = np.concatenate([keypoints, spine_keypoints], axis=1)
            scores = np.concatenate([scores, spine_scores], axis=1)
            return keypoints, scores

        self.pose_model = forward

    def __call__(self, image: np.ndarray):
        bboxes = self.det_model(image)
        keypoints, scores = self.pose_model(image, bboxes=bboxes)

        return keypoints, scores
