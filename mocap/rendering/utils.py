import os

import cv2
import numpy as np
import pandas as pd


def df_from_trc(trc_path):
    """
    Retrieve header and data from TRC file path.
    """
    df_header = pd.read_csv(
        trc_path, sep="\t", skiprows=1, header=None, nrows=2, encoding="ISO-8859-1"
    )
    header = dict(zip(df_header.iloc[0].tolist(), df_header.iloc[1].tolist()))

    df_lab = pd.read_csv(trc_path, sep="\t", skiprows=3, nrows=1)
    labels = df_lab.columns.tolist()[2:-1:3]
    labels_XYZ = np.array(
        [
            [labels[i] + "_X", labels[i] + "_Y", labels[i] + "_Z"]
            for i in range(len(labels))
        ]
    ).flatten()
    labels_FTXYZ = np.concatenate((["Frame#", "Time"], labels_XYZ))

    data = pd.read_csv(
        trc_path, sep="\t", skiprows=5, index_col=False, header=None, names=labels_FTXYZ
    )
    return header, data


def export_video(image_dir, video_output_path, fps=30):
    """
    Create a video from images in the image directory and save it as MP4.
    """
    img_array = []
    image_files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".png")],
        key=lambda x: int(x.split(".")[0]),
    )

    for filename in image_files:
        img = cv2.imread(os.path.join(image_dir, filename))
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    out = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    for img in img_array:
        out.write(img)

    out.release()
