import json

import os
import cv2
from tqdm import tqdm
from rtmlib import YOLOX, RTMPose, draw_skeleton
# import onnxruntime as ort
import glob
import numpy as np

def estimation_2d_custom(videodir_path,pose_model_path =  r"C:\Users\Jeremias\Downloads\td-cc_rtmpose-l_coco41-384x288_float32.onnx",json_output_dir = '',device = 'cpu',backend = 'onnxruntime'):
    video_files = sorted(glob.glob(os.path.join(videodir_path, '*.mp4')))
    pose_model_size = (288, 384)
    kpt_thr = 0.5
    print('output_dir:',json_output_dir)
    det_model = YOLOX(
        onnx_model='https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip',
        model_input_size=(640, 640),
        backend=backend,
        device=device
    )
    
    pose_model = RTMPose(
        onnx_model=pose_model_path,
        model_input_size=pose_model_size,
        backend=backend,
        device=device
    )
    for video_file in video_files:
        video_name_without_ext = os.path.splitext(os.path.basename(video_file))[0]+"_json"
        cap = cv2.VideoCapture(video_file)
        frame_idx = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not os.path.exists(os.path.join(json_output_dir,video_name_without_ext)):
            os.makedirs(os.path.join(json_output_dir,video_name_without_ext))
        with tqdm(total=total_frames, desc=f'Processing {video_name_without_ext}') as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                json_file_path = os.path.join(json_output_dir,video_name_without_ext, f'{video_name_without_ext}_{frame_idx:06d}.json')
                if os.path.exists(json_file_path):
                    frame_idx += 1
                    pbar.update(1)
                    continue

                bboxes = det_model(frame)
                keypoints, scores = pose_model(frame, bboxes=bboxes)
                save_to_openpose(json_file_path, keypoints, scores)
                frame_idx += 1
                pbar.update(1)
        cap.release()
    return 

def save_to_openpose(json_file_path, keypoints, scores):
    '''
    Save the keypoints and scores to a JSON file in the OpenPose format

    INPUTS:
    - json_file_path: Path to save the JSON file
    - keypoints: Detected keypoints
    - scores: Confidence scores for each keypoint

    OUTPUTS:
    - JSON file with the detected keypoints and confidence scores in the OpenPose format
    '''

    # Prepare keypoints with confidence scores for JSON output
    nb_detections = len(keypoints)
    # print('results: ', keypoints, scores)
    detections = []
    for i in range(nb_detections): # nb of detected people
        keypoints_with_confidence_i = []
        for kp, score in zip(keypoints[i], scores[i]):
            keypoints_with_confidence_i.extend([kp[0].item(), kp[1].item(), score.item()])
        detections.append({
                    "person_id": [-1],
                    "pose_keypoints_2d": keypoints_with_confidence_i,
                    "face_keypoints_2d": [],
                    "hand_left_keypoints_2d": [],
                    "hand_right_keypoints_2d": [],
                    "pose_keypoints_3d": [],
                    "face_keypoints_3d": [],
                    "hand_left_keypoints_3d": [],
                    "hand_right_keypoints_3d": []
                })
            
    # Create JSON output structure
    json_output = {"version": 1.3, "people": detections}
    # Save JSON output for each frame
    json_output_dir = os.path.abspath(os.path.join(json_file_path, '..'))
    if not os.path.isdir(json_output_dir): os.makedirs(json_output_dir)
    with open(json_file_path, 'w') as json_file:
        json.dump(json_output, json_file)