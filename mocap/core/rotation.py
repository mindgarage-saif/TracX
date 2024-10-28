import json
import os
import shutil
import xml.etree.ElementTree as ET

import cv2
import numpy as np


def get_rotation(videoName, rotation_dict):
    for key, value in rotation_dict.items():
        if key in videoName:
            return int(value)
    return None


def rotate_videos(video_list, output_dir, camera_parameters):
    tree = ET.parse(os.path.expanduser(camera_parameters))
    root = tree.getroot()
    rotation_dict = {
        camera.get("serial"): camera.get("viewrotation")
        for camera in root.find("cameras")
    }
    for video in video_list:
        video_name = os.path.basename(video)
        rot = get_rotation(video_name, rotation_dict)
        cap = cv2.VideoCapture(video)
        ret, frame = cap.read()
        if not ret:
            continue
        # frame = Image.fromarray(frame)
        # frame = frame.rotate(rot, expand=True)
        # frame = np.array(frame)
        if rot == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rot == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rot == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        else:
            print(f"Rotation angle {rot} not supported")
            continue
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        # Get original video's width, height, and fps
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Create a VideoWriter object
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Define VideoWriter object for MP4 file
        out = cv2.VideoWriter(
            os.path.join(output_dir, video_name.split(".")[0] + "_rot.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (frame_width, frame_height),
        )

        # out = cv2.VideoWriter(os.path.join(output_dir, videoName +"_rot.avi"), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
        out.write(frame)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # frame = Image.fromarray(frame)
            # frame = frame.rotate(rot, expand=True)
            # frame = np.array(frame)
            if rot == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rot == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif rot == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            # Write the rotated frame to the new video file
            out.write(frame)

        # Release the VideoCapture and VideoWriter objects
        cap.release()

def rotate_video_monocular(video_list, output_dir, rotation):

    for video in video_list:
        video_name = os.path.basename(video)
        rot = rotation
        cap = cv2.VideoCapture(video)
        ret, frame = cap.read()
        if not ret:
            continue
        # frame = Image.fromarray(frame)
        # frame = frame.rotate(rot, expand=True)
        # frame = np.array(frame)
        if rot == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rot == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rot == -90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        else:
            print(f"Rotation angle {rot} not supported")
            continue
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        # Get original video's width, height, and fps
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Create a VideoWriter object
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Define VideoWriter object for MP4 file
        out = cv2.VideoWriter(
            os.path.join(output_dir, video_name.split(".")[0] + "_rot.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (frame_width, frame_height),
        )

        # out = cv2.VideoWriter(os.path.join(output_dir, videoName +"_rot.avi"), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
        out.write(frame)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # frame = Image.fromarray(frame)
            # frame = frame.rotate(rot, expand=True)
            # frame = np.array(frame)
            if rot == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rot == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif rot == -90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            # Write the rotated frame to the new video file
            out.write(frame)

        # Release the VideoCapture and VideoWriter objects
        cap.release()





def unrotate_pose2d(pose_dir, camera_parameters):
    # Rename the original directory and create a new directory
    rotated_dir = pose_dir + "_rotated"
    os.rename(pose_dir, rotated_dir)
    os.makedirs(pose_dir, exist_ok=True)

    # Parse the camera parameters file
    tree = ET.parse(os.path.expanduser(camera_parameters))
    root = tree.getroot()

    # Create a dictionary mapping camera serial numbers to view rotation angles
    rotation_dict = {
        camera.get("serial"): camera.get("viewrotation")
        for camera in root.find("cameras")
    }

    rotated_poses = [
        os.path.join(rotated_dir, f)
        for f in os.listdir(rotated_dir)
        if os.path.isdir(os.path.join(rotated_dir, f))
    ]

    for rotated in rotated_poses:
        name = os.path.basename(rotated)
        unrotated = os.path.join(pose_dir, name)
        os.makedirs(unrotated, exist_ok=True)

        # Get a list of all JSON files in the directory
        pose_files = [f for f in os.listdir(rotated) if f.endswith(".json")]

        rotation_angle = get_rotation(name, rotation_dict)
        for file in pose_files:
            with open(os.path.join(rotated, file), "r") as f:
                data = json.load(f)
                for i in range(len(data["people"])):
                    # Extract the 'pose_keypoints_2d' data for the first person
                    keypoints = data["people"][i]["pose_keypoints_2d"]

                    # Split the keypoints into x, y coordinates and confidence values
                    x = keypoints[::3]
                    y = keypoints[1::3]
                    c = keypoints[2::3]

                    # Check the directory name against the dictionary to determine the rotation angle
                    if rotation_angle == 270:
                        y2 = np.array(keypoints[::3])
                        x2 = 1920 - np.array(keypoints[1::3])
                    elif rotation_angle == 90:
                        x2 = np.array(keypoints[1::3])
                        y2 = 1088 - np.array(keypoints[::3])
                    elif rotation_angle == 180:
                        x2 = 1920 + np.array(keypoints[::3]) * -1
                        y2 = 1088 - np.array(keypoints[1::3])
                    else:
                        print(f"Rotation angle {rotation_angle} not supported")
                        continue

                    # Unrotate the points
                    points = np.array(list(zip(x2, y2)))
                    if rotation_angle == 90:
                        rotated_keypoints = [
                            coord
                            for i in range(len(points))
                            for coord in [
                                points[i][0],
                                points[i][1],
                                c[i],
                            ]
                        ]
                    elif rotation_angle == 180:
                        rotated_keypoints = [
                            coord
                            for i in range(len(points))
                            for coord in [
                                points[i][0],
                                points[i][1],
                                c[i],
                            ]
                        ]
                    elif rotation_angle == 270:
                        rotated_keypoints = [
                            coord
                            for i in range(len(points))
                            for coord in [
                                points[i][0],
                                points[i][1],
                                c[i],
                            ]
                        ]

                    # Write the modified data back to the file
                    data["people"][i]["pose_keypoints_2d"] = rotated_keypoints

            # Write the modified data to the new file
            unrotated_file = os.path.join(unrotated, file)
            with open(unrotated_file, "w") as f:
                json.dump(data, f)

    # Delete the rotated directory
    shutil.rmtree(rotated_dir)
