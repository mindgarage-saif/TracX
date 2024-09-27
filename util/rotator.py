import cv2
import numpy as np
import argparse
import os
import xml.etree.ElementTree as ET
from scipy import ndimage
from PIL import Image
# Open the video file
def get_rotation(videoName, rotation_dict):
    for key, value in rotation_dict.items():
        if key in videoName:
            return float(value)
    return None
def rotate(video_list,output_dir,camera_parameters):
    tree = ET.parse(os.path.expanduser(camera_parameters))
    root = tree.getroot()
    rotation_dict = {camera.get('serial'): camera.get('viewrotation') for camera in root.find('cameras')}
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
            raise ValueError(f"Rotation angle {rot} not supported")
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        # Get original video's width, height, and fps
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Create a VideoWriter object
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Define VideoWriter object for MP4 file
        out = cv2.VideoWriter(os.path.join(output_dir, video_name.split('.')[0] +"_rot.mp4"), cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        #out = cv2.VideoWriter(os.path.join(output_dir, videoName +"_rot.avi"), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
        out.write(frame)
        while(cap.isOpened()):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rotate videos')
    parser.add_argument('--input_dir', type=str, help='Input directory containing videos')
    parser.add_argument('camera_parameters', type=str, help='Path to the camera parameters XML file')
    parser.add_argument('--output_dir', type=str, help='Output directory to save rotated videos')
    args = parser.parse_args()
    rotate(args.input_dir, args.output_dir, args.camera_parameters)