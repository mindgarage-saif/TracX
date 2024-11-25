import os

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as ort
import pandas as pd
from matplotlib.animation import FuncAnimation

from mocap.constants import APP_ASSETS


def read_trc(file_path):
    """
    Reads a TRC file and parses it into a structured format.

    Parameters:
        file_path (str): Path to the TRC file.

    Returns:
        List[Dict]: A list of dictionaries with the following structure:
                    [
                        {
                            "keypoint_ids": [int],
                            "keypoint_names": [str],
                            "keypoints": np.array(K, 3),  # K is the number of time steps, 3 for X, Y, Z
                        }
                    ]
    """
    # Read metadata to extract keypoint names
    header_df = pd.read_csv(file_path, sep="\t", skiprows=3, nrows=0)
    keypoint_names = header_df.columns[2::3].tolist()

    # Assign keypoint IDs
    keypoint_ids = list(range(len(keypoint_names)))

    # Read motion capture data
    data_df = pd.read_csv(file_path, sep="\t", skiprows=4)
    frame_col = data_df.iloc[:, 0]
    time_col = data_df.iloc[:, 1]
    keypoint_coordinates = data_df.drop(data_df.columns[[0, 1]], axis=1)

    # Organize keypoint data into a structured format
    structured_data = []
    for idx, keypoint_name in enumerate(keypoint_names):
        frame = frame_col
        time = time_col
        x = keypoint_coordinates.iloc[:, idx * 3].to_numpy()
        y = keypoint_coordinates.iloc[:, idx * 3 + 1].to_numpy()
        z = keypoint_coordinates.iloc[:, idx * 3 + 2].to_numpy()
        keypoints = np.stack((frame, time, x, y, z), axis=1)
        structured_data.append(keypoints)

    structured_data = np.array(structured_data)  # (K, V, 5)
    structured_data = np.transpose(structured_data, (1, 0, 2))

    # Convert to a list of dictionaries
    return [
        {
            "frame": keypoints[:, 0],
            "time": keypoints[:, 1],
            "keypoint_ids": keypoint_ids,
            "keypoint_names": keypoint_names,
            "keypoints": keypoints[:, 2:],
        }
        for keypoints in structured_data
    ]


def normalize_data(data, res_w, res_h):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def lift_to_3d(model, keypoints, res_w, res_h):
    # Prepare input data
    keypoints = np.array(keypoints, dtype=np.float32)[:, :2]
    keypoints = normalize_data(keypoints, res_w, res_h)
    keypoints = keypoints.reshape(1, -1)

    # Run model
    onnx_input = {"l_x_": keypoints}
    output = model.run(None, onnx_input)

    # Post-process output
    depth = output[0][0].reshape(16, 3)[:, 2]
    return np.hstack((keypoints.reshape(16, 2), depth.reshape(16, 1)))


def create_animation(
    keypoints3d_list, joint_names, connections, output_path="animation.mp4"
):
    """
    Create a 3D animation of the stick figure.

    Parameters:
        keypoints3d_list (list): List of 3D keypoints arrays for each frame.
        joint_names (list): List of joint names corresponding to the keypoints.
        connections (list): List of connections between joints for the stick figure.
        output_path (str): Path to save the animation as a video file.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Compute one min/max for all frames
    keypoints3d_all = np.concatenate(keypoints3d_list, axis=0)
    x_min, y_min, z_min = np.min(keypoints3d_all, axis=0)
    x_max, y_max, z_max = np.max(keypoints3d_all, axis=0)
    min_lim = min(x_min, y_min, z_min)
    max_lim = max(x_max, y_max, z_max)
    ax.set_xlim(min_lim, max_lim)
    ax.set_ylim(min_lim, max_lim)
    ax.set_zlim(min_lim, max_lim)

    # Labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    def update(frame_idx):
        ax.clear()
        ax.set_xlim(min_lim, max_lim)
        ax.set_ylim(min_lim, max_lim)
        ax.set_zlim(min_lim, max_lim)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        keypoints3d = keypoints3d_list[frame_idx]

        for connection in connections:
            joint1 = joint_names.index(connection[0])
            joint2 = joint_names.index(connection[1])
            ax.plot(
                [keypoints3d[joint1][0], keypoints3d[joint2][0]],
                [keypoints3d[joint1][2], keypoints3d[joint2][2]],
                [keypoints3d[joint1][1], keypoints3d[joint2][1]],
                "ro-",
            )

        # Show 2D keypoints in blue
        for i, keypoint in enumerate(keypoints3d):
            ax.scatter(keypoint[0], keypoint[2], keypoint[1], c="b", s=50)

    ani = FuncAnimation(fig, update, frames=len(keypoints3d_list), interval=100)
    plt.show()


def update_trc(input_path, output_path, updated_keypoints):
    """
    Updates the 3D keypoints in a TRC file and saves the updated TRC file.

    Parameters:
        input_path (str): Path to the original TRC file.
        output_path (str): Path to save the updated TRC file.
        updated_keypoints (list): A list of updated 3D keypoints arrays of shape (N, V, 3),
                                  where N is the number of frames, V is the number of keypoints,
                                  and 3 corresponds to X, Y, Z coordinates.
    """
    # Read the original TRC file
    with open(input_path, "r") as f:
        lines = f.readlines()

    # Extract header and data
    header = lines[:5]  # First 5 lines are header

    # Parse header to get the column structure
    col_names = pd.read_csv(input_path, sep="\t", skiprows=3, nrows=0).columns
    num_columns = len(col_names)
    num_keypoints = (num_columns - 2) // 3  # Exclude Frame# and Time columns

    # Validate updated_keypoints shape
    if updated_keypoints.shape[1] != num_keypoints:
        raise ValueError(
            f"Updated keypoints have {updated_keypoints.shape[1]} keypoints, "
            f"but the TRC file has {num_keypoints} keypoints."
        )

    # Parse data lines into a DataFrame
    data_df = pd.read_csv(input_path, sep="\t", skiprows=4)
    frame_col = data_df.iloc[:, 0]
    time_col = data_df.iloc[:, 1]

    # Update keypoint columns with new values
    updated_data = np.zeros((updated_keypoints.shape[0], num_columns))
    updated_data[:, 0] = frame_col  # Frame column
    updated_data[:, 1] = time_col  # Time column

    # Flatten keypoints and update DataFrame
    updated_keypoints_flat = updated_keypoints.reshape(
        updated_keypoints.shape[0], -1
    )  # (N, V*3)
    updated_data[:, 2:] = updated_keypoints_flat

    # Create updated DataFrame
    updated_df = pd.DataFrame(updated_data, columns=col_names)

    # Save updated TRC file
    with open(output_path, "w") as f:
        # Write header
        f.writelines(header)

        # Write updated data
        updated_df.to_csv(f, sep="\t", index=False)


if __name__ == "__main__":
    structured_data = read_trc(
        "data/projects/3D_LIFTING/Ex4_gan_1_Sports2D/Ex4_gan_1_Sports2D_px_person00.trc"
    )

    # Load lifting model
    model_path = os.path.join(APP_ASSETS, "models", "lifting", "baseline.onnx")
    model = ort.InferenceSession(model_path)

    mapping = [0, 1, 2, 3, 7, 8, 9, 13, 15, 14, 16, 17, 18, 19, 20, 21]
    joint_names = [
        "Hip",
        "RHip",
        "RKnee",
        "RAnkle",
        "LHip",
        "LKnee",
        "LAnkle",
        "Neck",
        "Head",
        "Nose",
        "RShoulder",
        "RElbow",
        "RWrist",
        "LShoulder",
        "LElbow",
        "LWrist",
    ]
    connections = [
        ["Hip", "RHip"],
        ["RHip", "RKnee"],
        ["RKnee", "RAnkle"],
        ["Hip", "LHip"],
        ["LHip", "LKnee"],
        ["LKnee", "LAnkle"],
        ["Hip", "Neck"],
        ["Neck", "Nose"],
        ["Nose", "Head"],
        ["Neck", "RShoulder"],
        ["RShoulder", "RElbow"],
        ["RElbow", "RWrist"],
        ["Neck", "LShoulder"],
        ["LShoulder", "LElbow"],
        ["LElbow", "LWrist"],
    ]
    res_w = 2160
    res_h = 3840

    keypoints3d_list = []
    for frame_idx in range(len(structured_data)):
        keypoints = [structured_data[frame_idx]["keypoints"][i] for i in mapping]
        keypoints3d = lift_to_3d(model, keypoints, res_w, res_h)
        keypoints3d_list.append(keypoints3d)

    update_trc(
        "data/projects/3D_LIFTING/Ex4_gan_1_Sports2D/Ex4_gan_1_Sports2D_px_person00.trc",
        "data/projects/3D_LIFTING/Ex4_gan_1_Sports2D/Ex4_gan_1_Sports2D_px_person00_updated.trc",
        np.array(keypoints3d_list),
    )
