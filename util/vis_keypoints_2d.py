import json
import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
# Define the rotation matrices
rot90cw = np.array([[0, 1], [-1, 0]])  # 90 degrees clockwise
rot90ccw = np.array([[0, -1], [1, 0]])  # 90 degrees counterclockwise
rot180 = np.array([[-1, 0], [0, -1]])  # 180 degrees

def vis_json_mmpose(baseDir,xml_path,path_to_vid,rot: bool = True):
    p = 0
    cap = cv2.VideoCapture(path_to_vid)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rotation_dict = {camera.get('serial'): camera.get('viewrotation') for camera in root.find('cameras')}
    view_dict = {camera.get('serial'): (camera.find('fov_video_max').get('right'),camera.find('fov_video_max').get('bottom')) for camera in root.find('cameras')}
    for filename in os.listdir(baseDir):
        ret, frame = cap.read()
        if p%25 != 0:
            p += 1
            continue
        p += 1
        json_path = os.path.join(baseDir, filename)
        with open(json_path, 'r') as file:
            data = json.load(file)
            x = []
            y = []
            for person in data['people']:
                key_points = np.array(person['pose_keypoints_2d']).reshape(-1, 3)
                c = key_points[:,2]
                if not rot:
                    rotation_angle = rotation_dict.get(filename.split('.')[0])
                    width, height = view_dict.get(filename.split('.')[0])
                    if rotation_angle == '270':
                        y2 = np.array(key_points[:,0])
                        x2 = width - np.array(key_points[:,1]) # static 1920 for width of image
                    elif rotation_angle == '90':
                        x2 = np.array(key_points[:,1])
                        y2 = height - np.array(key_points[:,0]) # static 1088 for height of image
                    elif rotation_angle == '180':
                        x2 = (width + np.array(key_points[:,0])*-1)
                        y2 = height - np.array(key_points[:,1])
                    elif rotation_angle == '0':
                        x2 = np.array(key_points[:,0])
                        y2 = np.array(key_points[:,1])
                    else:
                        #continue  # skip this file if the directory name doesn't specify a rotation
                        print("no rotation")
                        continue
                else:
                    x2 = np.array(key_points[:,0])
                    y2 = np.array(key_points[:,1])
                x.extend(x2)
                y.extend(y2)
            # change bgr to rgb
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not ret:
                break
            plt.imshow(frame)
            plt.scatter(x, y, c='r')
            for t in range(len(x)):
                plt.text(x[t], y[t], str(t), fontsize=10, color='black')
            plt.show()
if __name__ == "__main__":
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument("--root_dir",default=r"E:\Uni\MonocularSystems\HiWi\experiments\Experiment_2024-09-17_20-33-36\pose\Generic Markerless 2_Miqus_6_28983_rot_json", type=str, help="Path to the directory containing the JSON files")
    argsparser.add_argument("--xml_path",default=r"E:\Uni\MonocularSystems\HiWi\Gait Markerless 2.settings_new.xml", type=str, help="Path to the camera XML file")
    argsparser.add_argument("--vid_path",default=r"E:\Uni\Data\LIHS\LIHS\ROM_2\ROM_2\Generic Markerless 2_Miqus_6_28983.avi", type=str, help="Path to the video")
    argsparser.add_argument("--rot",default=True, type=bool, help="Whether to rotate the keypoints")
    args = argsparser.parse_args()
    vis_json_mmpose(args.root_dir,args.xml_path,args.vid_path,args.rot)