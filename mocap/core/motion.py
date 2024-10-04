from copy import deepcopy

import numpy as np
import pandas as pd

from .skeletons import BaseSkeleton, Halpe26Skeleton, TheiaSkeleton


def get_range(vals):
    """Get the minimum and maximum values of a list of values, ignoring outliers.

    Returns:
        tuple(float, float): Minimum and maximum values.
    """
    # Calculate the IQR to filter out outliers
    q1 = np.percentile(vals, 25)
    q3 = np.percentile(vals, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Filter out the outliers
    bounded_vals = [x for x in vals if lower_bound <= x <= upper_bound]

    # Return the minimum and maximum of the filtered X coordinates
    if bounded_vals:
        return min(bounded_vals), max(bounded_vals)
    else:
        # In case all points are filtered out, return the min and max of the original data
        return min(vals), max(vals)


def df_from_trc(trc_path):
    """
    Retrieve header and data from TRC file path.
    """
    df_header = pd.read_csv(
        trc_path, sep="\t", skiprows=1, header=None, nrows=2, encoding="ISO-8859-1"
    )
    header = dict(zip(df_header.iloc[0].tolist(), df_header.iloc[1].tolist()))

    df_lab = pd.read_csv(trc_path, sep="\t", skiprows=3, nrows=1)
    labels = df_lab.columns.tolist()[2:-1:3]
    labels_XYZ = np.array(
        [
            [labels[i] + "_X", labels[i] + "_Y", labels[i] + "_Z"]
            for i in range(len(labels))
        ]
    ).flatten()
    labels_FTXYZ = np.concatenate((["Frame#", "Time"], labels_XYZ))

    data = pd.read_csv(
        trc_path, sep="\t", skiprows=5, index_col=False, header=None, names=labels_FTXYZ
    )
    return header, data


class MotionSequence:
    def __init__(self, skeleton: BaseSkeleton, fps: int, name: str = None):
        self.skeleton: BaseSkeleton = skeleton
        self.name = name
        self.fps = fps
        self.frames = []

    def set_frame(self, frame_idx, pose, metadata=None):
        skeleton = deepcopy(self.skeleton)
        skeleton.set_pose(pose)

        self.frames.append((frame_idx, skeleton, metadata))

    def get_xlimits(self):
        mins = []
        maxs = []
        for _, skeleton, _ in self.frames:
            x_min, x_max = skeleton.x_range
            mins.append(x_min)
            maxs.append(x_max)

        x_min = get_range(mins)[0]
        x_max = get_range(maxs)[1]
        return x_min, x_max

    def get_ylimits(self):
        mins = []
        maxs = []
        for _, skeleton, _ in self.frames:
            y_min, y_max = skeleton.y_range
            mins.append(y_min)
            maxs.append(y_max)

        y_min = get_range(mins)[0]
        y_max = get_range(maxs)[1]
        return y_min, y_max

    def get_zlimits(self):
        mins = []
        maxs = []
        for _, skeleton, _ in self.frames:
            z_min, z_max = skeleton.z_range
            mins.append(z_min)
            maxs.append(z_max)

        z_min = get_range(mins)[0]
        z_max = get_range(maxs)[1]
        return z_min, z_max

    def __len__(self):
        return len(self.frames)

    def get_duration(self):
        return len(self) / self.fps

    def iterate_frames(self):
        self.frames.sort(key=lambda x: x[0])
        for frame_idx, skeleton, metadata in self.frames:
            yield frame_idx, skeleton, metadata

    @staticmethod
    def from_theia_json(path: str):
        import json

        # Load the JSON file
        with open(path, "r") as file:
            data = json.load(file)
        frames = data["frames"]

        # Initialize the motion object
        skeleton = TheiaSkeleton()
        fps = data["frameRate"]
        motion = MotionSequence(skeleton, fps)

        # Add frames to the motion object
        joint_names = [s["name"] for s in data["segments"]]
        for frame_idx, frame in enumerate(frames):
            # Extract the pose from the frame
            pose = {}
            for joint, position in zip(joint_names, frame["segmentPos"]):
                pose[joint] = position[0] / 1000, position[1] / 1000, position[2] / 1000

            # Add the frame to the motion object
            motion.set_frame(frame_idx, pose)

        return motion

    @staticmethod
    def from_pose2sim_trc(path: str):
        if not path.endswith(".trc"):
            raise ValueError("Input file must be a .trc file.")

        header, data = df_from_trc(path)
        bodyparts = np.array([d[:-2] for d in data.columns[2::3]])

        xs, ys, zs = None, None, None

        # Aggregate data for each frame
        for bp in bodyparts:
            bp_X = bp + "_X"
            bp_Y = bp + "_Y"
            bp_Z = bp + "_Z"
            if xs is None:
                xs = np.array(data[bp_X]).reshape(-1, 1)
                ys = np.array(data[bp_Y]).reshape(-1, 1)
                zs = np.array(data[bp_Z]).reshape(-1, 1)
            else:
                xs = np.concatenate((xs, np.array(data[bp_X]).reshape(-1, 1)), axis=1)
                ys = np.concatenate((ys, np.array(data[bp_Y]).reshape(-1, 1)), axis=1)
                zs = np.concatenate((zs, np.array(data[bp_Z]).reshape(-1, 1)), axis=1)

        # Initialize the motion object
        skeleton = Halpe26Skeleton()
        fps = int(header["DataRate"])
        motion = MotionSequence(skeleton, fps)

        # Add frames to the motion object
        for frame_idx in range(len(data)):
            pose = {}
            for i, bp in enumerate(bodyparts):
                pose[bp] = (zs[frame_idx, i], xs[frame_idx, i], ys[frame_idx, i])

            motion.set_frame(frame_idx, pose)

        return motion
