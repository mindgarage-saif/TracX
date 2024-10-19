from rtmlib import PoseTracker, Body, Wholebody, BodyWithFeet, draw_skeleton
import os
import glob
import json
import logging
import itertools as it
from tqdm import tqdm
import numpy as np
import cv2
import onnxruntime as ort
import torch
import matplotlib.pyplot as plt
joint_to_joint_conections = [
    (0,1),(1,2),(2,3),(0,4),(4,5),(5,6),(0,7),(7,8),(8,9),(7,10),(10,11),(11,12),(7,13),(13,14),(14,15)
]
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

def normalize_data(data, res_w=1920, res_h=1080):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)

def estimation_3d(keypoints_dir,out_put,MODEL,res_w=1920, res_h=1080):
    json_files = sorted(glob.glob(os.path.join(keypoints_dir, '*.json')))
    data_3d_dic = {}
    for i,json_file in enumerate(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)
        keypoints = np.array(data['people'][0]['pose_keypoints_2d']).reshape(-1, 3)
        data_2d = np.array(keypoints[[19,12,14,16,11,13,15,18,0,17,5,7,9,6,8,10],:2],dtype=np.float32)
        input2 = normalize_data(data_2d,res_w,res_h)
        input2 = input2.reshape(1,-1)
        onnx_input = {
            "l_x_": input2
        }

        output = MODEL.run(None,onnx_input)
        res = output[0][0].reshape(16,3)
        data_3d_dic[i] = res.tolist()
    with open(os.path.join(out_put,'3d_data.json'),'w') as f:
        json.dump(data_3d_dic,f)

def estimation_2d(video_path,mode = 'lightweight',json_output_dir = '',device = 'cpu',backend = 'auto'):
    print("Estimation 2d")
    video_name_wo_ext = os.path.basename(video_path).split(".")[0]
    ModelClass = BodyWithFeet
    try:
        pose_tracker = PoseTracker(
            ModelClass,
            det_frequency=1,
            mode=mode,
            backend=backend,
            device=device,
            tracking=False,
            to_openpose=False)
    except Exception as e:
        print(f"Could not load model: {e}")
        raise
    try:
        cap = cv2.VideoCapture(video_path)
    except:
        print(f"Could not open video file: {video_path}")
        raise
    res_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    res_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_idx = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    #plt.ion()
    with tqdm(total=total_frames, desc=f'Processing {os.path.basename(video_path)}') as pbar:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            keypoints, scores = pose_tracker(frame)
            json_file_path = os.path.join(json_output_dir, f'{video_name_wo_ext}_{frame_idx:06d}.json')
            save_to_openpose(json_file_path, keypoints, scores)
            frame_idx += 1
            pbar.update(1)
    cap.release()
    return res_w, res_h ,fps
def moncular_estimation(video_path, mode = 'lightweight',json_output_dir = '',pose3d_dir=''):
    try:
        if torch.cuda.is_available() and 'CUDAExecutionProvider' in ort.get_available_providers():
            device = 'cuda'
            backend = 'onnxruntime'
            logging.info(f"\nValid CUDA installation found: using ONNXRuntime backend with GPU.")
        else:
            raise 
    except:
        try:
            if 'MPSExecutionProvider' in ort.get_available_providers() or 'CoreMLExecutionProvider' in ort.get_available_providers():
                device = 'mps'
                backend = 'onnxruntime'
                logging.info(f"\nValid MPS installation found: using ONNXRuntime backend with GPU.")
            else:
                raise
        except:
            device = 'cpu'
            backend = 'openvino'
            logging.info(f"\nNo valid CUDA installation found: using OpenVINO backend with CPU.")
    MODEL = ort.InferenceSession(r"C:\Users\Jeremias\Downloads\basline_model_MB.onnx",providers=['CPUExecutionProvider'])
    print("Model loaded")
    res_w, res_h ,fps = estimation_2d(video_path, mode, json_output_dir=json_output_dir,device=device,backend=backend)
    estimation_3d(json_output_dir,MODEL,res_w,res_h)

if __name__ == "__main__":
    try:
        if torch.cuda.is_available() and 'CUDAExecutionProvider' in ort.get_available_providers():
            device = 'cuda'
            backend = 'onnxruntime'
            logging.info(f"\nValid CUDA installation found: using ONNXRuntime backend with GPU.")
        else:
            raise 
    except:
        try:
            if 'MPSExecutionProvider' in ort.get_available_providers() or 'CoreMLExecutionProvider' in ort.get_available_providers():
                device = 'mps'
                backend = 'onnxruntime'
                logging.info(f"\nValid MPS installation found: using ONNXRuntime backend with GPU.")
            else:
                raise
        except:
            device = 'cpu'
            backend = 'openvino'
            logging.info(f"\nNo valid CUDA installation found: using OpenVINO backend with CPU.")
    video_path = r"E:\Uni\MonocularSystems\HiWi\test.mp4"
    json_output_dir = r"E:\Uni\MonocularSystems\HiWi\test_output"
    mode = 'lightweight'
    res_w, res_h ,fps = estimation_2d(video_path, mode,  json_output_dir=json_output_dir,device=device,backend=backend)