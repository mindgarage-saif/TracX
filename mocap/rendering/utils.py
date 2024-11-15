import os

import cv2


def export_video(image_dir, video_output_path, fps=30):
    """Create a video from images in the image directory and save it as MP4."""
    frames = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".png")],
        key=lambda x: int(x.split(".")[0]),
    )

    # Get size from first image
    img = cv2.imread(os.path.join(image_dir, frames[0]))
    height, width, _ = img.shape
    size = (width, height)

    writer = cv2.VideoWriter(
        video_output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size
    )
    for fn in frames:
        frame = cv2.imread(os.path.join(image_dir, fn))
        writer.write(frame)

    writer.release()
