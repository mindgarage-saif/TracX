import logging
import os

import cv2
import numpy as np
import toml


def rot_vec(rotation_matrix: np.ndarray) -> list:
    """
    Converts a rotation matrix to a rotation vector.

    Args:
        rotation_matrix (np.ndarray): A 3x3 rotation matrix.

    Returns:
        list: A 3-element list representing the rotation vector."""
    rot = cv2.Rodrigues(rotation_matrix)[0].reshape(-1)
    return rot.tolist()


def scale_intrinsics(K: np.ndarray, image_size: tuple) -> np.ndarray:
    """
    Scale the intrinsic matrix K to the image size if it is normalized.

    Args:
        K (np.ndarray): The intrinsic matrix.
        image_size (tuple): The size of the image in pixels.

    Returns:
        np.ndarray: The scaled intrinsic matrix.
    """
    fx, fy = K[0,0], K[1,1]
    cx, cy = K[0,2], K[1,2]
    is_normalized = (cx <= 1 and cy <= 1)
    if is_normalized:
        # Unnormalize K by image size
        S = (image_size[0], image_size[1])
        fx *= S[0]
        fy *= S[1]
        cx *= S[0]
        cy *= S[1]
        K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
    return K


def import_wearhealth_camera(calibration_file: str, image_size: tuple) -> dict:
    """
    Parses the calibration text file and returns a Pose2Sim-compatible
    dictionary containing intrinsic and extrinsic camera parameters.

    Args:
        calibration_file (str): The path to the calibration file.
        image_size (tuple): The size of the image in pixels

    Returns:
        dict: A dictionary containing the camera parameters
    """
    with open(calibration_file, "r") as file:
        lines = file.readlines()

    sections = {}
    current_section = None
    data = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # Skip empty lines
        if stripped.endswith("Translation"):
            if current_section:
                sections[current_section] = data
                data = []
            current_section = "Translation"
        elif stripped.endswith("Rotation"):
            if current_section:
                sections[current_section] = data
                data = []
            current_section = "Rotation"
        elif stripped.endswith("Intrinsische Parameter"):
            if current_section:
                sections[current_section] = data
                data = []
            current_section = "Intrinsische Parameter"
        elif stripped.endswith("Projektionsmatrix"):
            if current_section:
                sections[current_section] = data
                data = []
            current_section = "Projektionsmatrix"
        else:
            data.append(stripped)

    # Add the last section
    if current_section and data:
        sections[current_section] = data

    # Convert extracted data to appropriate numpy arrays
    t = np.array([float(x) for x in sections.get("Translation", [])])

    rotation = []
    for line in sections.get("Rotation", []):
        rotation.extend([float(x) for x in line.split()])
    R = np.array(rotation).reshape((3, 3))

    # Compute a rotation vector from the rotation matrix
    rotation_vector = rot_vec(R)

    intrinsic = []
    for line in sections.get("Intrinsische Parameter", []):
        intrinsic.extend([float(x) for x in line.split()])
    K = np.array(intrinsic).reshape((3, 3))

    projection = []
    for line in sections.get("Projektionsmatrix", []):
        projection.extend([float(x) for x in line.split()])
    P = np.array(projection).reshape((3, 4))

    # Compute a projection matrix from the intrinsic and extrinsic parameters
    extrinsics = np.hstack((R, t.reshape(3, 1)))
    P_computed = K.dot(extrinsics)  # P = K[R|t]

    # Compare and show a warning if the computed projection matrix is different
    # from the extracted projection matrix
    inverted = not np.allclose(P, P_computed, atol=1e-6)
    if inverted:
        R = R.T
        t = -R @ t
        extrinsics = np.hstack((R, t.reshape(3, 1)))
        P_computed = K.dot(extrinsics)  # P = K[R|t]

    if not np.allclose(P, P_computed, atol=1e-6):
        logging.warning(
            "Computed projection matrix differs from the extracted projection matrix despite adjusting for inversion. "
            "This discrepancy may affect the accuracy of triangulation and other calculations."
        )

    return {
        "name": os.path.basename(calibration_file).split(".")[0],
        "size": image_size,
        "matrix": scale_intrinsics(K, image_size),
        "distortions": np.zeros(4),
        "rotation": rotation_vector,
        "translation": t,
        "projection_matrix": P_computed,
        "fisheye": False,
    }


def import_wearhealth_cameras(calibration_dir, image_size):
    # Find all .txt files
    calibration_files = [
        os.path.join(calibration_dir, f)
        for f in os.listdir(calibration_dir)
        if f.endswith(".txt")
    ]

    out_str = ""
    for calibration_file in calibration_files:
        calibration_data = import_wearhealth_camera(calibration_file, image_size)
        out_str += f"[{calibration_data['name']}]\n"
        out_str += toml.dumps(calibration_data, encoder=toml.TomlNumpyEncoder()) + "\n"

    return out_str


if __name__ == "__main__":
    calibration_dir = "data/wearhealth/calibration/matrices"
    calibration_toml = import_wearhealth_cameras(calibration_dir, image_size=(1300, 900))
    calibration_file_toml = os.path.join(
        os.path.dirname(calibration_dir), "calibration.toml"
    )
    with open("calibration.toml", "w") as f:
        f.write(calibration_toml)
