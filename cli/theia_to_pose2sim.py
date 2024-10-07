import argparse
import json
import os

import numpy as np
import pandas as pd


def theia_to_pose2sim(theia_file, seq_name, f_range):
    # Load Theia JSON file
    with open(theia_file, "r") as file:
        data = json.load(file)

    # Read motion data
    frames = data["frames"]
    Q_P = np.array([f["segmentPos"] for f in frames])[f_range[0] : f_range[1], :]

    for i in range(len(Q_P)):
        for j in range(len(Q_P[i])):
            if Q_P[i][j][0] == None:
                Q_P[i][j] = [0, 0, 0]

    # Convert from mm to m
    Q_P = Q_P / 1000

    Q_rotated = Q_P.copy()
    Q_rotated[:, :, [0, 1, 2]] = Q_P[:, :, [1, 2, 0]]
    Q = Q_rotated[:, 1:]

    trc_f = f"{seq_name}_{f_range[0]}-{f_range[1]}.trc"
    keypoints_names = [
        "RHip",
        "RKnee",
        "RAnkle",
        "LHip",
        "LKnee",
        "LAnkle",
        "Neck",
        "RShoulder",
        "RElbow",
        "RWrist",
        "LShoulder",
        "LElbow",
        "LWrist",
        "Nose",
    ]

    # Header
    DataRate = CameraRate = OrigDataRate = frame_rate = 60
    NumFrames = len(Q)
    NumMarkers = len(Q[0])
    header_trc = [
        "PathFileType\t4\t(X/Y/Z)\t" + trc_f,
        "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames",
        "\t".join(
            map(
                str,
                [
                    DataRate,
                    CameraRate,
                    NumFrames,
                    NumMarkers,
                    "m",
                    OrigDataRate,
                    f_range[0],
                    f_range[1],
                ],
            )
        ),
        "Frame#\tTime\t" + "\t\t\t".join(keypoints_names) + "\t\t",
        "\t\t"
        + "\t".join([f"X{i+1}\tY{i+1}\tZ{i+1}" for i in range(len(keypoints_names))]),
    ]

    q_prime = pd.DataFrame(Q.reshape(Q.shape[0], -1))
    q_prime.index = np.array(range(0, f_range[1] - f_range[0])) + 1
    q_prime.insert(0, "t", q_prime.index / frame_rate)

    pose3d_dir = os.path.join("./", "pose-3d" + seq_name)
    if not os.path.exists(pose3d_dir):
        os.mkdir(pose3d_dir)

    # Write TRC file
    trc_path = os.path.realpath(os.path.join(pose3d_dir, trc_f))
    with open(trc_path, "w") as trc_o:
        [trc_o.write(line + "\n") for line in header_trc]
        q_prime.to_csv(trc_o, sep="\t", index=True, header=None, lineterminator="\n")
    return trc_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("theia_file", help="Theia JSON file")
    parser.add_argument("seq_name", help="Sequence name")
    parser.add_argument("f_range", nargs=2, type=int, help="Frame range")
    args = parser.parse_args()

    theia_to_pose2sim(args.theia_file, args.seq_name, args.f_range)
