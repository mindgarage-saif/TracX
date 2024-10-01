import argparse
import json
import os

import numpy as np
import pandas as pd


def theijsonTotrc(seq_name, f_range, json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
    frames = data["frames"]
    Q_P = np.array([frame["segmentPos"] for frame in frames])[
        f_range[0] : f_range[1], :
    ]
    for i in range(len(Q_P)):
        for j in range(len(Q_P[i])):
            if Q_P[i][j][0] == None:
                Q_P[i][j] = [0, 0, 0]
    Q_P = Q_P / 1000  # convert from mm to m
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
    pose3d_dir = os.path.join("./", "pose-3d" + seq_name)
    if not os.path.exists(pose3d_dir):
        os.mkdir(pose3d_dir)
    trc_path = os.path.realpath(os.path.join(pose3d_dir, trc_f))
    q_prime = pd.DataFrame(Q.reshape(Q.shape[0], -1))
    q_prime.index = np.array(range(0, f_range[1] - f_range[0])) + 1
    q_prime.insert(0, "t", q_prime.index / frame_rate)
    with open(trc_path, "w") as trc_o:
        [trc_o.write(line + "\n") for line in header_trc]
        q_prime.to_csv(trc_o, sep="\t", index=True, header=None, lineterminator="\n")
    print(f"{trc_f} saved to {pose3d_dir}")
    return trc_path


if __name__ == "__main__":
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument(
        "--file_name", default="ROM_2", type=str, help="Sequence name"
    )
    argsparser.add_argument("--f_start", default=0, type=int, help="Frame start")
    argsparser.add_argument("--f_end", default=-1, type=int, help="Frame end")
    argsparser.add_argument(
        "--json_path",
        default=r"E:\Uni\Data\LIHS\LIHS\ROM_2\ROM_2\Generic Markerless 2-3d-data.json",
        type=str,
        help="Path to the JSON file",
    )
    args = argsparser.parse_args()
    theijsonTotrc(args.file_name, [args.f_start, args.f_end], args.json_path)
