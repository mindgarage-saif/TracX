import os

import cv2


def export_video(image_dir, video_output_path, fps=30):
    """Create a video from images in the image directory and save it as MP4."""
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
