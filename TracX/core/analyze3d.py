import os

import numpy as np
import onnxruntime as ort
import pandas as pd

from TracX.constants import APP_ASSETS
from TracX.utils import read_trc


def normalize_data(data, res_w, res_h):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def lift_keypoints(model, keypoints, res_w, res_h):
    # Map keypoints to H3.6M order
    mapping = [0, 1, 2, 3, 7, 8, 9, 13, 15, 14, 16, 17, 18, 19, 20, 21]
    reverse_mapping = {original: i for i, original in enumerate(mapping)}

    keypoints_mapped = [keypoints[i] for i in mapping]

    # Prepare input data
    keypoints_input = np.array(keypoints_mapped, dtype=np.float32)[:, :2]
    keypoints_input = normalize_data(keypoints_input, res_w, res_h)
    keypoints_input = keypoints_input.reshape(1, -1)

    # Run model
    onnx_input = {"l_x_": keypoints_input}
    output = model.run(None, onnx_input)

    # Post-process output
    depth = output[0][0].reshape(16, 3)[:, 2]

    # Map back to the original order
    keypoints_3d = []
    for i in range(len(keypoints)):
        if i in reverse_mapping:
            # Replace with the lifted keypoints (including depth)
            keypoint_index = reverse_mapping[i]
            keypoints_3d.append(np.append(keypoints[i][:2], depth[keypoint_index]))
        else:
            # Keep the original 2D keypoint, append depth as 0 (or any default value)
            keypoints_3d.append(np.append(keypoints[i][:2], 0.0))

    return np.array(keypoints_3d, dtype=np.float32)


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

    # Make Frame# column integer
    updated_df["Frame#"] = updated_df["Frame#"].astype(int)

    # Save updated TRC file
    with open(output_path, "w") as f:
        # Write header
        f.writelines(header)

        # Write updated data
        updated_df.to_csv(f, sep="\t", index=False, header=False)

    # Print the LBigToe and two following columns for the first row
    lbigtoe_index = col_names.get_loc("LBigToe")
    print(updated_df.iloc[0, lbigtoe_index : lbigtoe_index + 3].tolist())


def lift_2d_to_3d(input_path, output_path, res_w, res_h):
    pose2d = read_trc(input_path)

    # Load lifting model
    model_path = os.path.join(APP_ASSETS, "models", "lifting", "baseline.onnx")
    model = ort.InferenceSession(model_path)

    pose3d = []
    for frame_idx in range(len(pose2d)):
        kpts_2d = pose2d[frame_idx]["keypoints"]
        kpts_3d = lift_keypoints(model, kpts_2d, res_w, res_h)
        pose3d.append(kpts_3d)

    update_trc(
        input_path,
        output_path,
        np.array(pose3d),
    )
