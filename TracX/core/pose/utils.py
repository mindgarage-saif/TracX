import json
import os


def save_to_openpose(json_file_path, keypoints, scores):
    """Save the keypoints and scores to a JSON file in the OpenPose format

    INPUTS:
    - json_file_path: Path to save the JSON file
    - keypoints: Detected keypoints
    - scores: Confidence scores for each keypoint

    OUTPUTS:
    - JSON file with the detected keypoints and confidence scores in the OpenPose format
    """
    # Prepare keypoints with confidence scores for JSON output
    nb_detections = len(keypoints)
    detections = []
    for i in range(nb_detections):  # nb of detected people
        keypoints_with_confidence_i = []
        for kp, score in zip(keypoints[i], scores[i]):
            keypoints_with_confidence_i.extend(
                [kp[0].item(), kp[1].item(), score.item()],
            )
        detections.append(
            {
                "person_id": [-1],
                "pose_keypoints_2d": keypoints_with_confidence_i,
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": [],
                "pose_keypoints_3d": [],
                "face_keypoints_3d": [],
                "hand_left_keypoints_3d": [],
                "hand_right_keypoints_3d": [],
            },
        )

    # Create JSON output structure
    json_output = {"version": 1.3, "people": detections}

    # Save JSON output for each frame
    json_output_dir = os.path.abspath(os.path.join(json_file_path, ".."))
    if not os.path.isdir(json_output_dir):
        os.makedirs(json_output_dir)
    with open(json_file_path, "w") as json_file:
        json.dump(json_output, json_file)
