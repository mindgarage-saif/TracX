import numpy as np
import pandas as pd


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
