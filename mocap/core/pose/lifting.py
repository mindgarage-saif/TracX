import glob
import json
import os

import numpy as np
import onnxruntime as ort


def normalize_data(data, res_w=1920, res_h=1080):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def lift_to_3d(model_path, keypoints_dir, out_put, res_w, res_h):
    MODEL = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    json_files = sorted(glob.glob(os.path.join(keypoints_dir, "*.json")))
    data_3d_dic = {}
    for i, json_file in enumerate(json_files):
        with open(json_file) as f:
            data = json.load(f)
        keypoints = np.array(data["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
        data_2d = np.array(
            keypoints[[19, 12, 14, 16, 11, 13, 15, 18, 0, 17, 5, 7, 9, 6, 8, 10], :2],
            dtype=np.float32,
        )
        input2 = normalize_data(data_2d, res_w, res_h)
        input2 = input2.reshape(1, -1)
        onnx_input = {"l_x_": input2}

        output = MODEL.run(None, onnx_input)
        res = output[0][0].reshape(16, 3)
        data_3d_dic[i] = res.tolist()

    with open(os.path.join(out_put, "3d_data.json"), "w") as f:
        json.dump(data_3d_dic, f)
