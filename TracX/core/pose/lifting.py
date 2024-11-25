import glob
import json
import logging
import os

import numpy as np
import onnxruntime as ort
from tqdm import tqdm


def normalize_data(data, res_w, res_h):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def lift_to_3d(model_path, keypoints_dir, out_put, res_w, res_h):
    # Load 2D to 3D lifting model
    logging.info("Loading 2D to 3D lifting model...")
    model = ort.InferenceSession(model_path)

    # Log model inputs and outputs for debugging
    logging.debug("Model inputs:")
    for input in model.get_inputs():
        logging.debug(f"  {input.name}: {input.shape} {input.type}")
    logging.debug("Model outputs:")
    for output in model.get_outputs():
        logging.debug(f"  {output.name}: {output.shape} {output.type}")

    # Find 2D pose files
    logging.info(f"Looking for 2D pose files in {keypoints_dir}...")
    json_files = sorted(glob.glob(os.path.join(keypoints_dir, "*.json")))

    # Process 2D pose files
    logging.info(f"Lifting {len(json_files)} 2D poses to 3D...")
    pose3d = {}
    for i, json_file in enumerate(tqdm(json_files, desc="Lifting 2D to 3D")):
        with open(json_file) as f:
            data = json.load(f)

        # Extract 2D keypoints (FIXME: Only works for one person)
        keypoints = np.array(data["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
        data_2d = np.array(
            keypoints[[19, 12, 14, 16, 11, 13, 15, 18, 0, 17, 5, 7, 9, 6, 8, 10], :2],
            dtype=np.float32,
        )
        input2 = normalize_data(data_2d, res_w, res_h)
        input2 = input2.reshape(1, -1)
        onnx_input = {"l_x_": input2}

        output = model.run(None, onnx_input)
        res = output[0][0].reshape(16, 3)
        pose3d[i] = res.tolist()

    # Save 3D poses to file
    logging.info(f"Saving 3D poses to {out_put}...")
    with open(os.path.join(out_put, "3d_data.json"), "w") as f:
        json.dump(pose3d, f)
