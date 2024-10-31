import logging
import os
from typing import Type

import cv2
import onnxruntime as ort
from Pose2Sim import Pose2Sim
from rtmlib import BodyWithFeet, PoseTracker
from tqdm import tqdm

from .solutions2d import BodyWithSpine
from .utils import save_to_openpose


def process_video(
    video_path: str,
    save_dir: str,
    model_class: Type,
    model_mode: str,
    overwrite: bool = False,
    backend: str = "onnxruntime",
    device: str = "cpu",
):
    # Load the model
    try:
        pose_tracker = PoseTracker(
            model_class,
            mode=model_mode,
            det_frequency=1,
            tracking=False,
            to_openpose=False,
            backend=backend,
            device=device,
        )
    except Exception as e:
        error = f"Failed to load {model_class} in {model_mode} mode: {e}"
        raise Exception(error)

    # Open the video file
    try:
        cap = cv2.VideoCapture(video_path)
    except Exception as e:
        error = f"Failed to open video file: {e}"
        raise Exception(error)

    # Get video metadata
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create save directory
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_save_dir = os.path.join(save_dir, video_name + "_json")
    os.makedirs(video_save_dir, exist_ok=True)

    # Process the video
    frame_idx = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    with tqdm(
        total=total_frames,
        desc=f"Processing {video_name}",
    ) as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Define save file path
            save_path = os.path.join(
                video_save_dir, f"{video_name}_{frame_idx:06d}.json"
            )

            # Skip if overwrite True and frame already processed
            if overwrite and os.path.exists(save_path):
                frame_idx += 1
                pbar.update(1)
                continue

            # Estimate 2D keypoints
            keypoints, scores = pose_tracker(frame)

            # Save keypoints in OpenPose format
            save_to_openpose(save_path, keypoints, scores)

            # Update progress bar
            frame_idx += 1
            pbar.update(1)

    # Release video capture
    cap.release()

    # Return video metadata
    return width, height, fps


def process_folder(
    video_dir: str,
    save_dir: str,
    model_class: Type,
    model_mode: str,
    video_format="mp4",
    overwrite: bool = False,
    backend: str = "onnxruntime",
    device: str = "cpu",
):
    # Get list of video files
    video_files = [
        os.path.join(video_dir, f)
        for f in os.listdir(video_dir)
        if os.path.isfile(os.path.join(video_dir, f))
        and f.lower().endswith(video_format.lower())
    ]

    # Process each video file
    output = None
    for video_file in video_files:
        output = process_video(
            video_path=video_file,
            save_dir=save_dir,
            model_class=model_class,
            model_mode=model_mode,
            overwrite=overwrite,
            backend=backend,
            device=device,
        )

    default_values = (1920, 1080, 30)
    return output or default_values


class PoseTracker2D:
    @staticmethod
    def _select_backend():
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers:
            device = "cuda"
            backend = "onnxruntime"
            logging.info("Using ONNXRuntime backend with GPU (CUDA).")
        elif (
            "MPSExecutionProvider" in providers
            or "CoreMLExecutionProvider" in providers
        ):
            device = "mps"
            backend = "onnxruntime"
            logging.info("Using ONNXRuntime backend with GPU (MPS/CoreML).")
        else:
            device = "cpu"
            backend = "onnxruntime"
            logging.info("Using ONNXRuntime backend with CPU.")

        return backend, device

    @staticmethod
    def estimateDefault():
        Pose2Sim.poseEstimation()

    @staticmethod
    def estimateCustom(
        videos,
        save_dir,
        model_class,
        model_mode,
        video_format="mp4",
        overwrite=False,
    ):
        backend, device = PoseTracker2D._select_backend()

        # Check if videos is a directory
        if os.path.isdir(videos):
            return process_folder(
                video_dir=videos,
                save_dir=save_dir,
                model_class=model_class,
                model_mode=model_mode,
                video_format=video_format,
                overwrite=overwrite,
                backend=backend,
                device=device,
            )

        # Check if videos is a file
        if os.path.isfile(videos):
            return process_video(
                video_path=videos,
                model_class=BodyWithSpine,
                model_mode=model_mode,
                save_dir=save_dir,
                backend=backend,
                device=device,
                overwrite=overwrite,
            )

        # Invalid input
        raise Exception("Invalid input for videos.")

    @staticmethod
    def estimateBodyWithSpine(
        videos,
        save_dir,
        video_format="mp4",
        overwrite=False,
    ):
        return PoseTracker2D.estimateCustom(
            videos=videos,
            save_dir=save_dir,
            model_class=BodyWithSpine,
            model_mode="performance",
            video_format=video_format,
            overwrite=overwrite,
        )

    @staticmethod
    def estimateBodyWithFeet(
        videos,
        save_dir,
        video_format="mp4",
        overwrite=False,
    ):
        return PoseTracker2D.estimateCustom(
            videos=videos,
            save_dir=save_dir,
            model_class=BodyWithFeet,
            model_mode="lightweight",
            video_format=video_format,
            overwrite=overwrite,
        )
