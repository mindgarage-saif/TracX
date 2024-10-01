import argparse
import os

import cv2
import numpy as np


def blur(path, region, blur_size, output):
    # Open the video file
    cap = cv2.VideoCapture(path)

    # Get original video's width, height, and fps
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create a VideoWriter object
    out = cv2.VideoWriter(
        output,
        cv2.VideoWriter_fourcc("M", "J", "P", "G"),
        fps,
        (frame_width, frame_height),
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            # Define the region to blur (top left corner to bottom right corner)
            # For example, let's blur the region from (100, 100) to (200, 200)
            roi = frame[region[0] : region[1], region[2] : region[3]]

            # Apply a blur filter to the region
            roi = cv2.blur(roi, blur_size, cv2.BORDER_DEFAULT)

            # Replace the original region with the blurred region
            frame[region[0] : region[1], region[2] : region[3]] = roi

            # Write the modified frame to the new video file
            out.write(frame)
        else:
            break

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()


if __name__ == "__main__":
    argsPars = argparse.ArgumentParser()
    argsPars.add_argument(
        "--path", default=r"./video.avi", type=str, help="Path to the video file"
    )
    argsPars.add_argument(
        "--region",
        nargs=4,
        type=int,
        help="Region to blur (top left corner to bottom right corner)",
    )
    argsPars.add_argument(
        "--blur_size", nargs=2, type=int, help="Size of the blur filter"
    )
    argsPars.add_argument(
        "--output",
        default=r"./video_blur.avi",
        type=str,
        help="Path to the output video file",
    )
    args = argsPars.parse_args()
    blur(args.path, tuple(args.region), tuple(args.blur_size), args.output)
