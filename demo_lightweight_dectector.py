"""
This script uses the following pipeline:
1. Hand detection
2. Draw bounding boxes around hands

For CPU: pip install opencv-python rtmlib onnxruntime (~110 FPS)
For GPU: pip install opencv-python rtmlib onnxruntime-gpu  (~250 FPS)
"""
import time

import cv2
import numpy as np
from rtmlib import Hand, draw_bbox


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


def create_lightweight_detector():
    return Hand(
        mode="lightweight",
        backend="onnxruntime",
        device="cpu",  # or "cuda" if onnxruntime-gpu is installed
    ).det_model


def lightweight_demo(detector, camera_id):
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
detector = create_lightweight_detector()

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
lightweight_demo(detector, camera_id)
