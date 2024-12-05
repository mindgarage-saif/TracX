import json
import logging
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


def rotate_video(video_file, rot, save_dir=None):
    rot = 270 if rot == -90 else rot
    if rot not in [90, 180, 270]:
        error = f"Rotation angle {rot} not supported. Skipping video."
        logging.error(error)
        raise ValueError(error)

    def read_format(video_path):
        return video_path.split(".")[-1].lower()

    supported_formats = {
        "mp4": cv2.VideoWriter_fourcc(*"mp4v"),
        "avi": cv2.VideoWriter_fourcc(*"XVID"),
        "mov": cv2.VideoWriter_fourcc(*"mp4v"),
    }

    video_format = read_format(video_file)
    if video_format not in supported_formats:
        logging.error(f"Video format '{video_format}' not supported. Skipping video.")
        return None

    def rotate_frame(frame, rot):
        if rot == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        if rot == 90:
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if rot == 270:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        return None

    # Open the video file
    logging.info(f"Rotating video '{video_file}' by {rot} degrees.")
    cap = cv2.VideoCapture(video_file)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a VideoWriter object
    video_dir = os.path.dirname(video_file)
    video_name = os.path.basename(video_file)

    rotated_dir = save_dir if save_dir else video_dir
    rotated_file = os.path.join(
        rotated_dir, video_name.split(".")[0] + f"_rot.{video_format}"
    )
    # Set output frame size based on rotation
    if rot in [90, 270]:
        out = cv2.VideoWriter(
            rotated_file,
            supported_formats[video_format],
            cap.get(cv2.CAP_PROP_FPS),
            (height, width),  # Swapped dimensions for 90 and 270 degrees
        )
    else:
        out = cv2.VideoWriter(
            rotated_file,
            supported_formats[video_format],
            cap.get(cv2.CAP_PROP_FPS),
            (width, height),
        )

    # Process the video frame by frame
    logging.info(f"Processing video '{video_name}'...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = rotate_frame(frame, rot)
        if frame is None:
            logging.error(f"Rotation angle {rot} not supported. Skipping video.")
            break

        out.write(frame)

    cap.release()
    logging.info(f"Rotated video '{rotated_file}' saved.")
    return rotated_file


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
            logging.error(f"Rotation angle {rot} not supported")
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

        out.write(frame)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
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


def rotate_video_monocular(video_list, output_dir, rot):
    os.makedirs(output_dir, exist_ok=True)
    for video in video_list:
        rotate_video(video, rot, save_dir=output_dir)


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
            with open(os.path.join(rotated, file)) as f:
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
                        logging.error(f"Rotation angle {rotation_angle} not supported")
                        continue

                    # Unrotate the points
                    points = np.array(list(zip(x2, y2)))
                    if (
                        rotation_angle == 90
                        or rotation_angle == 180
                        or rotation_angle == 270
                    ):
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
