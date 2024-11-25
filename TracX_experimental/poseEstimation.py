import json
import os

import numpy as np

# 2D Pose for Each Camera
pose2d_dir = "data/projects/orthosuper-patient8-trial7/pose"
pose2d_dirs = [
    os.path.join(pose2d_dir, d)
    for d in sorted(os.listdir(pose2d_dir))
    if os.path.isdir(os.path.join(pose2d_dir, d))
]


def find_largest_person(people):
    largest_person = None
    for idx, person in enumerate(people):
        # x1, y1, c1, x2, y2, c2, ...
        pose_keypoints_2d = person["pose_keypoints_2d"]

        # Compute bounding box from pose keypoints
        x = pose_keypoints_2d[0::3]
        y = pose_keypoints_2d[1::3]
        x = [x[i] for i in range(len(x)) if pose_keypoints_2d[3 * i + 2] > 0.1]
        y = [y[i] for i in range(len(y)) if pose_keypoints_2d[3 * i + 2] > 0.1]
        if len(x) == 0 or len(y) == 0:
            continue

        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        area = (x_max - x_min) * (y_max - y_min)

        if largest_person is None or area > largest_person["area"]:
            largest_person = {
                "idx": idx,
                "area": area,
            }

    return largest_person["idx"] if largest_person is not None else 0


# Read 2D poses
pose2d = {}
for pose2d_dir in pose2d_dirs:
    for file in sorted(os.listdir(pose2d_dir)):
        with open(os.path.join(pose2d_dir, file), "r") as f:
            data = json.load(f)
            cam_id = int(os.path.basename(file).split(".")[0].split("_")[0])
            idx = find_largest_person(data["people"])

            if cam_id not in pose2d:
                pose2d[cam_id] = []

            frame_pose = np.array(data["people"][idx]["pose_keypoints_2d"]).reshape(
                -1, 3
            )
            pose2d[cam_id].append(frame_pose)

# Create a numpy array from the 2D poses with shape (views, frames, keypoints, 3)
pose2d = {cam_id: np.array(pose2d[cam_id]) for cam_id in pose2d}
pose2d = dict(sorted(pose2d.items()))
pose2d = np.stack([pose2d[cam_id] for cam_id in pose2d], axis=0)
print(pose2d.shape)  # (views, frames, keypoints, 3)

# Save 2D pose in a npy file
np.save("pose2d.npy", pose2d)

# Assuming `pose2d` is a list of arrays, one for each view
# and `connections` is defined as a list of (kp1, kp2) pairs
visualize_grid(pose2d, connections)
