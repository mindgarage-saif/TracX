import json
from time import strftime
from typing import List, Optional

from mocap.core import Experiment
import os
import cv2
from tqdm import tqdm
from rtmlib import YOLOX, RTMPose, draw_skeleton
# import onnxruntime as ort
import glob
def create_experiment(
    video_files: List[str],
    calibration_file: str,
    experiment_name: Optional[str] = None,
) -> Experiment:
    # Create or load the experiment.
    experiment_name = experiment_name or strftime("%Y%m%d_%H%M%S")
    experiment = Experiment(experiment_name)

    # Add the video files.
    for video_file in video_files:
        experiment.add_video(video_file)

    # Make sure that at least one video file was added.
    if experiment.num_videos == 0:
        raise ValueError("No supported video files found")

    # Add the camera calibration file.
    experiment.set_camera_parameters(calibration_file)

    return experiment


# def execute_pipeline_mocular(
#         video_files: List[str],
#         experiment_name: Optional[str] = None,
# ):
#     """Run the full pipeline for a given set of video files and calibration file.

#     Args:
#         video_files (List[str]): List of paths to video files.
#         experiment_name (Optional[str], optional): Name of the experiment. Defaults to None.

#     Raises:
#         ValueError: If the config file is invalid or not a .toml file.

#     Note:
#         Assumes camera calibration to be in QCA camera format. It doesn't matter if it is in XML file
#         format or txt file format. But internally it has to be in QCA format.
#     """
#     # Initialize the experiment
#     print("Initializing experiment...")
#     if experiment_name is None:
#         experiment: Experiment = create_experiment(
#             video_files,
#             experiment_name=experiment_name,
#         )
#         print(f"Created {experiment} with {experiment.num_videos} video(s)")
#     else:
#         experiment = Experiment(experiment_name, create=False)
#     print(f"Experiment configuration: {json.dumps(experiment.cfg, indent=2)}")

#     print("Processing experiment data...")
#     experiment.process_mocular()


def execute_pipeline(
    video_files: List[str],
    calibration_file: str,
    correct_rotation=True,
    use_marker_augmentation=False,
    visualization_mode="opensim",
    visualization_args=dict(),
    experiment_name: Optional[str] = None,
):
    """Run the full pipeline for a given set of video files and calibration file.

    Args:
        video_files (List[str]): List of paths to video files.
        calibration_file (str): Path to the camera calibration file.
        correct_rotation (bool, optional): Whether to rotate the 2D poses. Defaults to False.
        use_marker_augmentation (bool, optional): Whether to use marker augmentation. Defaults to False.
        opensim (bool, optional): Whether to run OpenSim processing. Defaults to True.
        blender (bool, optional): Whether to run Blender processing. Defaults to False.
        experiment_name (Optional[str], optional): Name of the experiment. Defaults to None.

    Raises:
        ValueError: If the config file is invalid or not a .toml file.

    Note:
        Assumes camera calibration to be in QCA camera format. It doesn't matter if it is in XML file
        format or txt file format. But internally it has to be in QCA format.
    """
    # Initialize the experiment
    print("Initializing experiment...")
    if experiment_name is None:
        experiment: Experiment = create_experiment(
            video_files,
            calibration_file,
            experiment_name=experiment_name,
        )
        print(f"Created {experiment} with {experiment.num_videos} video(s)")
    else:
        experiment = Experiment(experiment_name, create=False)
        print(
            f"Loaded experiment '{experiment.name}' with {experiment.num_videos} video(s)"
        )
    print(f"Experiment configuration: {json.dumps(experiment.cfg, indent=2)}")

    print("Processing experiment data...")
    experiment.process(
        correct_rotation=correct_rotation,
        use_marker_augmentation=use_marker_augmentation,
    )

    print("Visualizing 3D motion...")
    experiment.visualize(
        mode=visualization_mode,
        **visualization_args,
    )

    print("Pipeline execution complete.")

def estimation_2d_custom(videodir_path,pose_model_path =  r"C:\Users\Jeremias\Downloads\td-cc_rtmpose-l_coco41-384x288_float32.onnx",json_output_dir = '',device = 'cpu',backend = 'onnxruntime'):
    video_files = sorted(glob.glob(os.path.join(videodir_path, '*.mp4')))
    pose_model_size = (288, 384)
    kpt_thr = 0.5
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
                bboxes = det_model(frame)
                keypoints, scores = pose_model(frame, bboxes=bboxes)
                json_file_path = os.path.join(json_output_dir,video_name_without_ext, f'{video_file}_{frame_idx:06d}.json')
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