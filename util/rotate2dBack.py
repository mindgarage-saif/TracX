import os
import json
import numpy as np
import shutil
import xml.etree.ElementTree as ET
import argparse

def get_rotation(videoName, rotation_dict):
    for key, value in rotation_dict.items():
        if key in videoName:
            return value
    return None


def rotate2dBack(baseDir,camera_parameters):
    listofDirs = os.listdir(baseDir)
    tree = ET.parse(os.path.expanduser(camera_parameters))
    root = tree.getroot()
    rotation_dict = {camera.get('serial'): camera.get('viewrotation') for camera in root.find('cameras')}
    for dir in listofDirs:
        print(dir)
        if not os.path.isdir(os.path.join(baseDir,dir)):
            continue
        # Get a list of all JSON files in the directory
        json_files = [f for f in os.listdir(os.path.join(baseDir , dir)) if f.endswith('.json')]

        new_dir = os.path.join(baseDir+"_rotated",dir)
        os.makedirs(new_dir, exist_ok=True)
        rotation_angle = get_rotation(os.path.basename(dir),rotation_dict)
        for file in json_files:
            with open(os.path.join(baseDir,dir, file), 'r') as f:
                data = json.load(f)
                for i in range(len(data['people'])):
                # Extract the 'pose_keypoints_2d' data for the first person
                    keypoints = data['people'][i]['pose_keypoints_2d']

                    # Split the keypoints into x, y coordinates and confidence values
                    x = keypoints[::3]
                    y = keypoints[1::3]
                    c = keypoints[2::3]

                    # Check the directory name against the dictionary to determine the rotation angle
                    if rotation_angle == '270':
                        y2 = np.array(keypoints[::3])
                        x2 = 1920 - np.array(keypoints[1::3])
                    elif rotation_angle == '90':
                        x2 = np.array(keypoints[1::3])
                        y2 = 1088 - np.array(keypoints[::3])
                    elif rotation_angle == '180':
                        x2 = (1920 + np.array(keypoints[::3])*-1)
                        y2 = 1088 - np.array(keypoints[1::3])
                    else:
                        raise ValueError(f"Rotation angle {rotation_angle} not supported")
                        continue  # skip this file if the directory name doesn't specify a rotation

                    # Rotate the points
                    
                    rotated_points = np.array(list(zip(x2, y2)))

                    #rotated_points = np.dot(points, rotation_matrix)
                    if rotation_angle == '90':
                        rotated_keypoints = [coord for i in range(len(rotated_points)) for coord in [rotated_points[i][0], rotated_points[i][1], c[i]]]
                    elif rotation_angle == '180':
                        rotated_keypoints = [coord for i in range(len(rotated_points)) for coord in [rotated_points[i][0] , rotated_points[i][1], c[i]]]
                    elif rotation_angle == '270':
                        rotated_keypoints = [coord for i in range(len(rotated_points)) for coord in [rotated_points[i][0] , rotated_points[i][1], c[i]]]
                    # Combine the rotated x and y coordinates and the confidence values back into the 'pose_keypoints_2d' format
                    #rotated_keypoints = []
                    #for i in range(len(rotated_points)):
                        #rotated_keypoints.extend([rotated_points[i][0], rotated_points[i][1], c[i]])

                    # Write the modified data back to the file
                    data['people'][i]['pose_keypoints_2d'] = rotated_keypoints

            # Create a copy of the original file
            new_file = os.path.join(new_dir, f"{os.path.splitext(file)[0]}{os.path.splitext(file)[1]}")
            shutil.copyfile(os.path.join(baseDir, dir, file), new_file)

            # Write the modified data to the new file
            with open(new_file, 'w') as f:
                json.dump(data, f)
    os.rename(baseDir, baseDir+"_old_unrotated")
if __name__ == '__main__':
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument("--baseDir",default=r"E:\Uni\MonocularSystems\HiWi\Data\experiments\new\LIHS\ROM2\pose", type=str, help="Base directory")
    argsparser.add_argument("--camer_parameters",default=r"E:\Uni\MonocularSystems\HiWi\Gait Markerless 2.settings_new.xml", type=str, help="Path to the camera XML file")
    args = argsparser.parse_args()

    rotate2dBack(args.baseDir,args.camer_parameters)