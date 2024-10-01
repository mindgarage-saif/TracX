import argparse
import json
import os
import xml.etree.ElementTree as ET

import numpy as np


def mmpose_cmu(directory, camera_xml, output_path):
    tree = ET.parse(camera_xml)
    root = tree.getroot()
    rotation_dict = {
        camera.get("serial"): camera.get("viewrotation")
        for camera in root.find("cameras")
    }
    view_dict = {
        camera.get("serial"): (
            camera.find("fov_video_max").get("right"),
            camera.find("fov_video_max").get("bottom"),
        )
        for camera in root.find("cameras")
    }
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a JSON file
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                data = json.load(f)

            for frame in data:
                bodies = []
                for instance in frame["instances"]:
                    c = instance["keypoint_scores"]
                    points = np.array(instance["keypoints"])
                    rotation_angle = rotation_dict.get(filename.split(".")[0])
                    width, height = view_dict.get(filename.split(".")[0])
                    if rotation_angle == "270":
                        y2 = np.array(points[:, 0])
                        x2 = width - np.array(
                            points[:, 1]
                        )  # static 1920 for width of image
                    elif rotation_angle == "90":
                        x2 = np.array(points[:, 1])
                        y2 = height - np.array(
                            points[:, 0]
                        )  # static 1088 for height of image
                    elif rotation_angle == "180":
                        x2 = width + np.array(points[:, 0]) * -1
                        y2 = height - np.array(points[:, 1])
                    else:
                        # continue  # skip this file if the directory name doesn't specify a rotation
                        print("no rotation")
                        continue
                    # rotated_points = np.dot(points, rotation_matrix)
                    rotated_points = np.array(list(zip(x2, y2)))
                    pose_keypoints_2d = [
                        coord
                        for i in range(len(rotated_points))
                        for coord in [rotated_points[i][0], rotated_points[i][1], c[i]]
                    ]
                    bodies.append({"pose_keypoints_2d": pose_keypoints_2d})

                new_data = {"version": 0.1, "people": bodies}
                os.makedirs(output_path, exist_ok=True)
                new_filename = (
                    f"{filename.split('.')[0]}_{frame['frame_id']:012d}_keypoints.json"
                )
                new_filepath = os.path.join(output_path, new_filename)

                with open(new_filepath, "w") as f:
                    json.dump(new_data, f)


if __name__ == "__main__":
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument(
        "--json_2d_path_mmpose",
        default=r"~/Documents/Pose2SimData/RTMPose-t/ROM_2_videos_rot",
        type=str,
        help="Path to the directory containing the JSON files",
    )
    argsparser.add_argument(
        "--xml_path",
        default=r"~/Documents/Pose2SimData/RTMPose-t/Gait Markerless 1.settings.xml",
        type=str,
        help="Path to the camera XML file",
    )
    argsparser.add_argument(
        "--output_path",
        default=r"~/Documents/Pose2SimData/RTMPose-t/ROM_2_videos_rot",
        type=str,
        help="Path to the output directory",
    )
    args = argsparser.parse_args()
    vis_json_mmpose(args.json_2d_path_mmpose, args.xml_path, args.output_path)
