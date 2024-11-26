import numpy as np
from rtmlib import YOLOX, RTMPose


class Face:
    MODE = {
        "lightweight": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_tiny_8xb8-300e_humanart-6f3252f9.zip",
            "det_input_size": (416, 416),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmpose-t_simcc-face6_pt-in1k_120e-256x256-df79d9a5_20230529.zip",
            "pose_input_size": (256, 256),
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
        Initialize the DFKI_Body43 pose estimation model.

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
        self.pose_model = RTMPose(
            pose,
            model_input_size=pose_input_size,
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
