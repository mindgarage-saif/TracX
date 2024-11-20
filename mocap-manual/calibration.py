import os

import cv2
import numpy as np


def to_rotation_vector(rotation_matrix):
    rot = cv2.Rodrigues(rotation_matrix)[0].reshape(-1)
    return rot.tolist()


def scale_intrinsics(K, image_width, image_height):
    """
    Scales the intrinsic matrix to the image size.
    """
    K_scaled = K.copy()
    K_scaled[0, 0] *= image_width  # fx_scaled = fx_normalized * W
    K_scaled[0, 1] *= image_height  # s_scaled = s_normalized * H
    K_scaled[0, 2] *= image_width  # cx_scaled = cx_normalized * W
    K_scaled[1, 1] *= image_height  # fy_scaled = fy_normalized * H
    K_scaled[1, 2] *= image_height  # cy_scaled = cy_normalized * H
    # K_scaled[2, :] remains [0, 0, 1]
    return K_scaled


def load_camera_calibration(file_path):
    """
    Parses the calibration text file and extracts Translation, Rotation,
    Intrinsic Parameters, and Projection Matrix.
    """
    with open(file_path, "r") as file:
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

    # Compute Euler angles from the rotation matrix
    rotation_angles = to_rotation_vector(R)

    intrinsic = []
    for line in sections.get("Intrinsische Parameter", []):
        intrinsic.extend([float(x) for x in line.split()])
    K = np.array(intrinsic).reshape((3, 3))
    K = scale_intrinsics(K, 1300, 900)

    projection = []
    for line in sections.get("Projektionsmatrix", []):
        projection.extend([float(x) for x in line.split()])
    P = np.array(projection).reshape((3, 4))

    # Compute a projection matrix from the intrinsic and extrinsic parameters
    extrinsics = np.hstack((R, t.reshape(3, 1)))
    P_computed = K.dot(extrinsics)  # P = K[R|t]

    # Compare and show a warning if the computed projection matrix is different
    # from the extracted projection matrix
    if not np.allclose(P, P_computed, atol=1e-6):
        print(
            "Warning: The computed projection matrix is different from the extracted projection matrix."
        )

    return {
        # "R": R,
        "size": (1300, 900),
        "matrix": K,
        "distortions": np.zeros(4),
        "rotation": rotation_angles,
        "translation": t,
        # "P": P,
        # "P'": P_computed,
    }


def to_toml(calibration_dir):
    import toml

    out_str = ""
    for idx in range(8):
        calibration_file = f"{calibration_dir}/{idx}.txt"
        calibration_data = load_camera_calibration(calibration_file)
        calibration_data["name"] = f"{idx}"
        calibration_data["fisheye"] = False

        out_str += f"[{idx}]\n"
        out_str += toml.dumps(calibration_data, encoder=toml.TomlNumpyEncoder()) + "\n"

    return out_str


if __name__ == "__main__":
    # Calibration Data
    calibration_dir = "data/projects/orthosuper-patient8-trial7/calibration/matrices"
    calibration_files = [
        os.path.join(calibration_dir, f)
        for f in os.listdir(calibration_dir)
        if f.endswith(".txt")
    ]

    # Read projection matrices
    projection_matrices = {}
    for file in sorted(calibration_files):
        with open(file, "r") as f:
            cam_id = int(os.path.basename(file).split(".")[0])
            projection_matrix = load_camera_calibration(file)["projection_matrix"]
            projection_matrices[cam_id] = projection_matrix
    projection_matrices = dict(sorted(projection_matrices.items()))
    print(
        "Camera IDs:", list(projection_matrices.keys())
    )  # Camera IDs: [0, 1, 2, 3, 4, 5, 6, 7]

    # Stack projection matrices into a numpy array with shape (views, 3, 4)
    projection_matrices = np.array(
        [projection_matrices[cam_id] for cam_id in sorted(projection_matrices.keys())]
    )
    print(projection_matrices.shape)  # (views, 3, 4)

    # Convert the calibration data to a TOML string
    calibration_toml = to_toml(calibration_dir)
    print(calibration_toml)

    # Save the calibration data to a TOML file
    with open("calibration.toml", "w") as f:
        f.write(calibration_toml)

    # Save the projection matrices to a numpy file
    np.save("projection_matrices.npy", projection_matrices)
