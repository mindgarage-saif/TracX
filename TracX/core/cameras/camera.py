import os

import cv2
import numpy as np
import toml


class Camera:
    """
    Represents a single camera with its calibration parameters.

    Attributes:
        id (str): Unique identifier for the camera.
        image_size (np.ndarray): Image size as [height, width].
        K (np.ndarray): Intrinsic camera matrix (3x3).
        dist (np.ndarray): Distortion coefficients (array of length 4 or 5).
        rotation_vector (np.ndarray): Rotation vector (3x1).
        translation_vector (np.ndarray): Translation vector (3x1).
        fisheye (bool): Flag indicating if fisheye distortion is used.
        optim_K (np.ndarray): Optimal new camera matrix for undistorting points (3x3).
        inv_K (np.ndarray): Inverse of the intrinsic camera matrix (3x3).
        R_mat (np.ndarray): Rotation matrix obtained from the rotation vector (3x3).
    """

    def __init__(self, config):
        """
        Initializes the Camera instance with calibration parameters.

        Args:
            config (dict): Calibration configuration dictionary for the camera.
        """
        self.id = config["name"]
        self.image_size = np.array(config.get("size", [1920, 1080]), dtype=int)
        self.K = np.array(
            config.get("matrix", [[0, 0, 0], [0, 0, 0], [0, 0, 1]]), dtype=float
        )
        self.dist = np.array(config.get("distortions", [0, 0, 0, 0]), dtype=float)
        self.rotation_vector = np.array(config.get("rotation", [0, 0, 0]), dtype=float)
        self.translation_vector = np.array(
            config.get("translation", [0, 0, 0]), dtype=float
        )
        self.fisheye = config.get("fisheye", False)

        # Compute the optimal new camera matrix for undistorting points
        self.optim_K, _ = cv2.getOptimalNewCameraMatrix(
            self.K, self.dist, tuple(self.image_size), 1, tuple(self.image_size)
        )

        # Compute the inverse of the intrinsic camera matrix
        self.inv_K = np.linalg.inv(self.K)

        # Convert rotation vector to rotation matrix
        self.R_mat, _ = cv2.Rodrigues(self.rotation_vector)

        if "projection_matrix" in config:
            self.P = np.array(config["projection_matrix"], dtype=float)
        else:
            self.P = self.compute_projection_matrix()

    def compute_projection_matrix(self, undistort=False):
        """
        Computes the projection matrix for the camera.

        Args:
            undistort (bool): If True, uses the optimal camera matrix for undistorting points.

        Returns:
            np.ndarray: Projection matrix (3x4).
        """
        if undistort:
            Kh = np.hstack([self.optim_K, np.zeros((3, 1))])
        else:
            Kh = np.hstack([self.K, np.zeros((3, 1))])

        # Construct the [R | T] matrix
        RT = np.hstack([self.R_mat, self.translation_vector.reshape(3, 1)])

        # Append a row [0, 0, 0, 1] to make it a 4x4 matrix
        H = np.vstack([RT, [0, 0, 0, 1]])

        # Compute the projection matrix
        return Kh @ H  # Resulting in a 3x4 matrix

    @property
    def intrinsic_parameters(self):
        """
        Returns the intrinsic parameters of the camera.

        Returns:
            dict: Dictionary containing intrinsic parameters.
        """
        return {
            "K": self.K,
            "optim_K": self.optim_K,
            "inv_K": self.inv_K,
            "dist": self.dist,
        }

    @property
    def extrinsic_parameters(self):
        """
        Returns the extrinsic parameters of the camera.

        Returns:
            dict: Dictionary containing extrinsic parameters.
        """
        return {
            "rotation_matrix": self.R_mat,
            "rotation_vector": self.rotation_vector,
            "translation_vector": self.translation_vector,
        }


class CameraSystem:
    """
    Represents a system of multiple cameras with their calibration parameters.

    Attributes:
        cameras (list of Camera): List of Camera instances in the system.
    """

    def __init__(self, calib_file):
        """
        Initializes the CameraSystem by loading calibration data from a TOML file.

        Args:
            calib_file (str): Path to the calibration TOML file.
        """
        self.calib_file = calib_file
        self.cameras = self._load_calibration(calib_file)

    def _load_calibration(self, calib_file):
        """
        Loads calibration parameters from a TOML file and initializes Camera instances.

        Args:
            calib_file (str): Path to the calibration TOML file.

        Returns:
            list of Camera: List of initialized Camera instances.
        """
        if not os.path.exists(calib_file):
            raise FileNotFoundError(f"Calibration file {calib_file} does not exist.")

        calib = toml.load(calib_file)

        # Filter out irrelevant keys and ensure we're only processing camera configurations
        cal_keys = [
            c
            for c in calib
            if c not in ["metadata", "capture_volume", "charuco", "checkerboard"]
            and isinstance(calib[c], dict)
        ]

        # Initialize Camera instances for each camera in the calibration file
        cameras = [Camera(calib[cam]) for cam in cal_keys]

        if not cameras:
            raise ValueError(
                "No valid camera configurations found in the calibration file."
            )

        return cameras

    def P(self, undistort=False):
        """
        Retrieves the projection matrices for all cameras in the system.

        Args:
            undistort (bool): If True, uses the optimal camera matrix for undistorting points.

        Returns:
            list of np.ndarray: List of projection matrices (each 3x4).
        """
        return [camera.P for camera in self.cameras]

    @property
    def K(self):
        """
        Retrieves the intrinsic matrices (K) for all cameras.

        Returns:
            list of np.ndarray: List of intrinsic matrices (3x3).
        """
        return [camera.K for camera in self.cameras]

    @property
    def dist(self):
        """
        Retrieves the distortion coefficients for all cameras.

        Returns:
            list of np.ndarray: List of distortion coefficients arrays.
        """
        return [camera.dist for camera in self.cameras]

    @property
    def R_mat(self):
        """
        Retrieves the rotation matrices for all cameras.

        Returns:
            list of np.ndarray: List of rotation matrices (3x3).
        """
        return [camera.R_mat for camera in self.cameras]

    @property
    def T(self):
        """
        Retrieves the translation vectors for all cameras.

        Returns:
            list of np.ndarray: List of translation vectors (3x1).
        """
        return [camera.translation_vector for camera in self.cameras]

    @property
    def image_sizes(self):
        """
        Retrieves the image sizes for all cameras.

        Returns:
            list of np.ndarray: List of image sizes as [height, width].
        """
        return [camera.image_size for camera in self.cameras]

    @property
    def camera_ids(self):
        """
        Retrieves the identifiers for all cameras.

        Returns:
            list of str: List of camera IDs.
        """
        return [camera.id for camera in self.cameras]

    def get_intrinsic_parameters(self):
        """
        Retrieves intrinsic parameters for all cameras.

        Returns:
            list of dict: List of dictionaries containing intrinsic parameters for each camera.
        """
        return [camera.intrinsic_parameters for camera in self.cameras]

    def get_extrinsic_parameters(self):
        """
        Retrieves extrinsic parameters for all cameras.

        Returns:
            list of dict: List of dictionaries containing extrinsic parameters for each camera.
        """
        return [camera.extrinsic_parameters for camera in self.cameras]
