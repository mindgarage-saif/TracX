import cv2
import numpy as np
import math
import os
from tqdm import tqdm

def create_video_grid(video_paths, output_path):
    """
    Create a grid video from multiple video files and save the output.

    Args:
    - video_paths (list): List of video file paths.
    - output_path (str): Path to save the output grid video.
    """
    # Read video information
    video_caps = [cv2.VideoCapture(vp) for vp in video_paths]
    if not all(cap.isOpened() for cap in video_caps):
        raise ValueError("One or more video files could not be opened.")

    # Ensure all videos have the same properties
    frame_width = int(video_caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(video_caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
    output_fps = int(video_caps[0].get(cv2.CAP_PROP_FPS))

    for cap in video_caps:
        if (int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) != frame_count):
            raise ValueError("All videos must have the same resolution and frame count.")

    # Determine grid size
    num_videos = len(video_paths)
    grid_cols = math.ceil(math.sqrt(num_videos))
    grid_rows = math.ceil(num_videos / grid_cols)

    # Output video writer
    grid_frame_width = grid_cols * frame_width
    grid_frame_height = grid_rows * frame_height
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(output_path, fourcc, output_fps, (grid_frame_width, grid_frame_height))

    print(f"Saving grid video to {output_path}...")

    # Read and write frames
    for frame_idx in tqdm(range(frame_count)):
        grid_frame = np.zeros((grid_frame_height, grid_frame_width, 3), dtype=np.uint8)

        for idx, cap in enumerate(video_caps):
            ret, frame = cap.read()
            if not ret:
                print(f"Error reading frame {frame_idx} from video {video_paths[idx]}.")
                continue

            # Resize frame to match grid dimensions
            aspect_ratio = frame_width / frame_height
            new_width = frame_width
            new_height = frame_height

            if frame.shape[1] / frame.shape[0] > aspect_ratio:
                new_height = int(frame.shape[0] * frame_width / frame.shape[1])
            else:
                new_width = int(frame.shape[1] * frame_height / frame.shape[0])

            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Create a black canvas and place the resized frame in the center
            padded_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            y_offset = (frame_height - new_height) // 2
            x_offset = (frame_width - new_width) // 2
            padded_frame[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

            frame = padded_frame

            row = idx // grid_cols
            col = idx % grid_cols
            y_start = row * frame_height
            y_end = y_start + frame_height
            x_start = col * frame_width
            x_end = x_start + frame_width

            grid_frame[y_start:y_end, x_start:x_end] = frame

        out_writer.write(grid_frame)

    # Release resources
    for cap in video_caps:
        cap.release()
    out_writer.release()
    print("Grid video saved successfully.")

if __name__ == "__main__":
    # Input: List of video file paths
    video_files = [
        "data/projects/M3D_SHARESPACE_T002/videos/C0008_CAM_0.MP4",
        "data/projects/M3D_SHARESPACE_T002/pose/C0008_CAM_0_pose.mp4",
        "data/projects/M3D_SHARESPACE_T002/output/stick_animation.mp4",
        "data/projects/M3D_SHARESPACE_T002/videos/C0008_CAM_1.MP4",
        "data/projects/M3D_SHARESPACE_T002/pose/C0008_CAM_1_pose.mp4",
        "ShareSpace_Pose2Sim_TwoCameras_OSIM.mp4",
    ]
    output_file = "grid_video.mp4"

    create_video_grid(video_files, output_file)
