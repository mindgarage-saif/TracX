"""
This script uses the following pipeline:
1. Person detection
2. Wholebody pose estimation including hands
3. Extract only hand keypoints
4. Compute bounding boxes for hands
5. Draw bounding boxes around hands

Significantly better performance, especially in egocentric views but speed is also slower.

For CPU: pip install opencv-python rtmlib onnxruntime  (~12 FPS)
For GPU: pip install opencv-python rtmlib onnxruntime-gpu  (~55 FPS)
"""
import time

import cv2
import numpy as np
from rtmlib import Wholebody, draw_bbox


def benchmark(detector, duration=5):
    """
    Benchmark the performance of a detector on dummy images.

    Args:
        detector (callable): The detector function to benchmark. It should take an image as input.
        duration (int): The duration in seconds for which to run the benchmark.

    Prints:
        Frames per second (FPS) achieved by the detector.
    """
    # Create a dummy image (fixed size, e.g., 640x480 with 3 channels)
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # Initialize counters
    start_time = time.time()
    frames_processed = 0

    # Run the benchmark for the specified duration
    while time.time() - start_time < duration:
        # Run the detector on the dummy image
        _ = detector(dummy_image)
        frames_processed += 1

    # Calculate elapsed time and FPS
    elapsed_time = time.time() - start_time
    fps = frames_processed / elapsed_time

    print(f"Benchmark completed: {frames_processed} frames processed in {elapsed_time:.2f} seconds.")
    print(f"FPS: {fps:.2f}")


def create_detector():
    pose_model = Wholebody(
        mode="lightweight",
        backend="onnxruntime",
        device="cuda",  # or "cuda" if onnxruntime-gpu is installed
    )

    def detector(frame):
        all_keypoints, all_scores = pose_model(frame)
        boxes = []

        num_hand_keypoints = 21
        l_start_id = 91
        r_start_id = 91 + num_hand_keypoints

        def pose_to_box(keypoints, scores):
            # Filter keypoints with valid scores
            valid_mask = scores > 0.5
            if not np.any(valid_mask):
                return None, 0  # No valid keypoints
            
            valid_keypoints = keypoints[valid_mask]
            x = valid_keypoints[:, 0]
            y = valid_keypoints[:, 1]
            score = scores[valid_mask].mean()
            return [x.min(), y.min(), x.max(), y.max()], score

        # Process left and right hand keypoints in a single loop
        for keypoints, scores in zip(all_keypoints, all_scores):
            # Extract left and right hand keypoints and scores
            l_keypoints = keypoints[l_start_id:l_start_id + num_hand_keypoints]
            r_keypoints = keypoints[r_start_id:r_start_id + num_hand_keypoints]
            l_scores = scores[l_start_id:l_start_id + num_hand_keypoints]
            r_scores = scores[r_start_id:r_start_id + num_hand_keypoints]

            # Compute bounding boxes for left and right hands
            for kpts, scs in [(l_keypoints, l_scores), (r_keypoints, r_scores)]:
                box, score = pose_to_box(kpts, scs)
                if box is not None:
                    boxes.append(box)

        return boxes

    return detector


def demo(detector, camera_id):
    # Find and initialize the camera device
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print("No camera found. Exiting.")
        exit(1)

    # Process the camera frames
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Exiting.")
                break

            # Perform hand detection
            boxes = detector(frame)

            # Draw bounding boxes on the frame
            draw_bbox(frame, boxes)

            # Display the frame
            cv2.imshow("Hand Detection", frame)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting on user request.")
                break
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

# Initialize the hand detector
print("Initializing hand detector...")
detector = create_detector()

# Run a benchmark to measure the performance of the detector
print("Running benchmark...")   
benchmark(detector)

# Ask if user wants to run a live demo or exit
print("Would you like to run a live demo? (y/n)")
response = input().lower()
if response != "y":
    print("Exiting.")
    exit(0)


# Run the live demo
print("Running live demo with camera 0...")
camera_id = 0
demo(detector, camera_id)
