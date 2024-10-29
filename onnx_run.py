import json

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as ort

MODEL = ort.InferenceSession(
    r"C:\Users\Jeremias\Downloads\basline_model_MB.onnx",
    providers=["CPUExecutionProvider"],
)


def unNormalizeData(normalized_data, data_mean, data_std):
    T = normalized_data.shape[0]  # Batch size
    D = data_mean.shape[0]  # 51
    print(T, D)
    orig_data = np.zeros((T, D), dtype=np.float32)

    orig_data = normalized_data

    # Multiply times stdev and add the mean
    stdMat = data_std.reshape((1, D))
    stdMat = np.repeat(stdMat, T, axis=0)
    meanMat = data_mean.reshape((1, D))
    meanMat = np.repeat(meanMat, T, axis=0)
    orig_data = np.multiply(orig_data, stdMat) + meanMat
    return orig_data


def normalize_data(data, res_w=1920, res_h=1080):
    data = data / res_w * 2 - [1, res_h / res_w]
    return data.astype(np.float32)


def main():
    # input_train,input_test,output_train,output_test,data_mean2d,data_std2d,data_mean3d, data_std3d,source_train,source_test = data_process.read_data("/netscratch/jkrauss/h36mVids/")
    # type(input_test)
    json_2d_Data = json.load(
        open(r"E:\Uni\MonocularSystems\HiWi\test_output\test_000041.json"),
    )
    data_2d = np.array(json_2d_Data["people"][0]["pose_keypoints_2d"])
    # print(data_2d.shape)
    x = np.array(data_2d[0::3])
    y = np.array(data_2d[1::3])
    x2 = x[[19, 11, 13, 15, 12, 14, 16, 18, 0, 17, 5, 7, 9, 6, 8, 10]]
    y2 = y[[19, 11, 13, 15, 12, 14, 16, 18, 0, 17, 5, 7, 9, 6, 8, 10]]

    input2 = np.array(list(zip(x2, y2)), dtype=np.float32)

    for i in range(1):
        # input = np.array(input).reshape(1,-1)
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # x = np.array(input[0][0::2])
        # y = np.array(input[0][1::2])
        # ax.scatter(x,y)
        # plt.show()
        input2 = normalize_data(input2)
        input2 = input2.reshape(1, -1)
        print(type(input2), input2.dtype)
        onnx_input = {"l_x_": input2}

        output = MODEL.run(None, onnx_input)
        # print(output)
        res = output[0][0].reshape(1, -1)
        print(res.shape)
        # outputs_unnorm = unNormalizeData(res, data_mean3d, data_std3d)
        res = res.reshape(16, 3)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(res[:, 0], res[:, 1], res[:, 2])
        ax.set_aspect("equal")
        plt.show()
        break


if __name__ == "__main__":
    main()
