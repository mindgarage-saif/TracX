import os

import numpy as np
from rtmlib import YOLOX, RTMPose

# FIXME: This import should not be here. Upload model somewhere online and add a link
from TracX.constants import APP_ASSETS


import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize


def refine_spine_keypoints(rough_keypoints, thoracic_count=12, lumbar_count=5):
    """
    Refines rough spine keypoints by applying smoothing, cubic splines, and optimization
    with anatomical constraints for thoracic and lumbar spine regions.
    
    Parameters:
        rough_keypoints (np.ndarray): Shape (1, K, 3), where K is the number of keypoints,
                                      and each keypoint has [x, y, confidence].
        thoracic_count (int): Number of thoracic spine keypoints.
        lumbar_count (int): Number of lumbar spine keypoints.
    
    Returns:
        refined_keypoints (np.ndarray): Shape (1, K, 2) with refined [x, y] coordinates.
    """
    # Extract x, y, and confidence
    keypoints = rough_keypoints[0, :, :2]  # Shape (K, 2)
    confidence = rough_keypoints[0, :, 2]  # Shape (K,)
    confidence = confidence / np.max(confidence)  # Normalize confidence

    # Split keypoints into thoracic and lumbar regions
    thoracic_keypoints = keypoints[:thoracic_count]
    lumbar_keypoints = keypoints[thoracic_count:]

    # Fit cubic splines for initial refinement
    x_thoracic = np.arange(thoracic_count)
    x_lumbar = np.arange(thoracic_count, thoracic_count + lumbar_count)
    spline_thoracic_x = CubicSpline(x_thoracic, thoracic_keypoints[:, 0])
    spline_thoracic_y = CubicSpline(x_thoracic, thoracic_keypoints[:, 1])
    spline_lumbar_x = CubicSpline(x_lumbar, lumbar_keypoints[:, 0])
    spline_lumbar_y = CubicSpline(x_lumbar, lumbar_keypoints[:, 1])

    # Combine splines into initial guess
    refined_thoracic = np.column_stack((spline_thoracic_x(x_thoracic), spline_thoracic_y(x_thoracic)))
    refined_lumbar = np.column_stack((spline_lumbar_x(x_lumbar), spline_lumbar_y(x_lumbar)))
    initial_guess = np.vstack((refined_thoracic, refined_lumbar))

    # Expected inter-vertebral distances (approximate values)
    expected_distances_thoracic = np.full(thoracic_count - 1, 2.0)  # Thoracic spacing
    expected_distances_lumbar = np.full(lumbar_count - 1, 2.5)      # Lumbar spacing

    # Define the loss function with anatomical constraints
    def loss_function(params):
        params = params.reshape(-1, 2)  # Convert flat array to (K, 2) for x, y
        thoracic = params[:thoracic_count]
        lumbar = params[thoracic_count:]

        # Smoothness penalty: Encourage a smooth curve (second derivatives)
        curvature_penalty = (
            np.sum(np.diff(thoracic[:, 0], n=2) ** 2) +
            np.sum(np.diff(thoracic[:, 1], n=2) ** 2) +
            np.sum(np.diff(lumbar[:, 0], n=2) ** 2) +
            np.sum(np.diff(lumbar[:, 1], n=2) ** 2)
        )

        # Inter-vertebral distance penalty
        distances_thoracic = np.sqrt(np.sum(np.diff(thoracic, axis=0) ** 2, axis=1))
        distances_lumbar = np.sqrt(np.sum(np.diff(lumbar, axis=0) ** 2, axis=1))
        distance_penalty = (
            np.sum((distances_thoracic - expected_distances_thoracic) ** 2) +
            np.sum((distances_lumbar - expected_distances_lumbar) ** 2)
        )

        # Weighted distance from rough keypoints
        distance_to_original = np.sum(confidence * np.sum((params - keypoints) ** 2, axis=1))

        # Total loss
        return distance_to_original + 0.1 * curvature_penalty + 0.5 * distance_penalty

    # Flatten initial guess for optimization
    initial_guess_flat = initial_guess.flatten()

    # Optimize keypoints with L-BFGS-B
    result = minimize(
        loss_function, initial_guess_flat, method='L-BFGS-B',
        options={'maxiter': 500, 'disp': False}
    )

    # Reshape optimized keypoints back to (K, 2)
    refined_keypoints = result.x.reshape(-1, 2)

    # Add batch dimension for compatibility
    return refined_keypoints[None, :, :]


def refine_spine_keypoints_batch(rough_keypoints):
    """
    Refines rough spine keypoints by smoothing, applying cubic splines, and optimizing for smoothness and closeness.
    
    Parameters:
        rough_keypoints (np.ndarray): Shape (B, K, 3), where B is the batch size, K is the number of keypoints, 
                                      and each keypoint has [x, y, confidence].
    Returns:
        refined_keypoints (np.ndarray): Shape (B, K, 2) with refined [x, y] coordinates.
    """
    refined_keypoints = []
    for i in range(rough_keypoints.shape[0]):
        rough_keypoints_i = rough_keypoints[i:i+1, :, :]
        refined_keypoints_i = refine_spine_keypoints(rough_keypoints_i)
        refined_keypoints.append(refined_keypoints_i)
        
    return np.concatenate(refined_keypoints, axis=0)


class BodyWithSpine:
    """
    BodyWithSpine class for human pose estimation using the DFKI_Body43 keypoint format.
    """

    # TODO: Train three versions of this model with 43 keypoints and update the links
    MODE = {
        "performance": {
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip",
            "det_input_size": (640, 640),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmpose-x_simcc-body7_pt-body7-halpe26_700e-384x288-7fb6e239_20230606.zip",
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
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_tiny_8xb8-300e_humanart-6f3252f9.zip",
            "det_input_size": (416, 416),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmpose-s_simcc-body7_pt-body7-halpe26_700e-256x192-7f134165_20230605.zip",
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
            "det": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_m_8xb8-300e_humanart-c2c7a14a.zip",
            "det_input_size": (640, 640),
            "pose": "https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmpose-m_simcc-body7_pt-body7-halpe26_700e-256x192-4d3e73dd_20230605.zip",
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
        mode: str = "performance",
        to_openpose: bool = False,
        backend="onnxruntime",
        device: str = "cpu",
        postprocess=False,
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
        self.postprocess = postprocess

        def forward(image, bboxes):
            keypoints, scores = self.body_model(image, bboxes=bboxes)
            spine_keypoints, spine_scores = self.spine_pose(image, bboxes=bboxes)
            spine_keypoints = spine_keypoints[:, -17:] 
            spine_scores = spine_scores[:, -17:]

            if self.postprocess:
                guessed_spine = np.concatenate([spine_keypoints, spine_scores[:, :, None]], axis=-1)
                spine_keypoints = refine_spine_keypoints_batch(guessed_spine)

            keypoints = np.concatenate([keypoints, spine_keypoints], axis=1)
            scores = np.concatenate([scores, spine_scores], axis=1)
            return keypoints, scores

        self.pose_model = forward

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
