import cv2
import threading
import time

import numpy as np

from .video import VideoCapture


class StereoCalibration:
    def __init__(self, left_camera_source: int, right_camera_source: int, sample_rate=24, max_frames=100):
        # Initialize video capture for both cameras
        self.left_camera = VideoCapture(left_camera_source, sample_rate)
        self.right_camera = VideoCapture(right_camera_source, sample_rate)

        # Store the frames captured from both cameras
        self.left_frames = []
        self.right_frames = []
        self.stereo_frames = []

        # Max frames to capture for calibration
        self.max_frames = max_frames

        # Flag to control synchronization and capturing
        self.capture_frames = True
        self.frame_count = 0

        # Synchronization lock
        self.lock = threading.Lock()

        # Calibration parameters
        self.calibration_params = None
        # You can change this to match your checkerboard dimensions
        self.checkerboard_size = (7, 6)
        # Termination criteria for corner sub-pixel accuracy
        self.criteria = (cv2.TERM_CRITERIA_EPS +
                         cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def start_capture(self):
        # Register event handlers
        self.left_camera.on_frame_captured(self._on_frame_captured_left)
        self.right_camera.on_frame_captured(self._on_frame_captured_right)

        # Start both cameras
        self.left_camera.start()
        self.right_camera.start()

    def stop_capture(self):
        # Stop both cameras
        self.left_camera.stop()
        self.right_camera.stop()

    def _on_frame_captured_left(self, frame, idx):
        with self.lock:
            if self.capture_frames:
                self.left_frames.append(frame)
                self._check_sync_and_save()

    def _on_frame_captured_right(self, frame, idx):
        with self.lock:
            if self.capture_frames:
                self.right_frames.append(frame)
                self._check_sync_and_save()

    def _check_sync_and_save(self):
        # Ensure both frames are captured before saving
        if len(self.left_frames) > 0 and len(self.right_frames) > 0:
            # Get synchronized frames
            left_frame = self.left_frames.pop(0)
            right_frame = self.right_frames.pop(0)

            self.stereo_frames.append((left_frame, right_frame))

            # Increment frame count and save the synchronized frames
            self.frame_count += 1
            print(f"Captured frame pair {self.frame_count}")

            # Check if max frames limit is reached
            if self.frame_count >= self.max_frames:
                self.capture_frames = False
                self.stop_capture()

    def run(self):
        self.start_capture()
        while self.capture_frames:
            time.sleep(1)  # Keep the main thread running while capturing
        self.stop_capture()

        # Calibrate the cameras
        calibration_left = self.calibrate_single([frame[0] for frame in self.stereo_frames])
        calibration_right = self.calibrate_single([frame[1] for frame in self.stereo_frames])
        stereo_calibration = self.calibrate_stereo(calibration_left, calibration_right)
        rectification = self.rectify(stereo_calibration, calibration_left[3])

        self.calibration_params = {
            "left": calibration_left[2],     # ret, mtx, dist, rvecs, tvecs
            "right": calibration_right[2],   # ret, mtx, dist, rvecs, tvecs
            "stereo": stereo_calibration,    # ret, mtx1, dist1, mtx2, dist2, R, T, E, F
            "rectification": rectification   # R1, R2, P1, P2, Q, roi1, roi2
        }

        # Save calibration parameters
        np.savez('calibration_params.npz', **self.calibration_params)
        print("Calibration complete and saved.")

    def calibrate_single(self, images):
        # Prepare object points, like (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
        checkerboard_size = self.checkerboard_size
        objp = np.zeros(
            (checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:checkerboard_size[0],
                               0:checkerboard_size[1]].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images
        objpoints = []  # 3D points in real-world space
        imgpoints = []  # 2D points in the image plane

        for img in images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chessboard corners
            ret, corners = cv2.findChessboardCorners(
                gray, checkerboard_size, None)

            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)

                # Refine the corners for better accuracy
                corners2 = cv2.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1), self.criteria)
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(
                    img, checkerboard_size, corners2, ret)
        #         cv2.imshow('img', img)
        #         cv2.waitKey(100)

        # cv2.destroyAllWindows()

        # Calibrate the camera
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)

        # Return the calibration results
        # np.savez('camera1_calibration.npz', ret=ret, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
        return objpoints, imgpoints, (ret, mtx, dist, rvecs, tvecs), gray.shape[::-1]

    def calibrate_stereo(self, calibration_left, calibration_right):
        objpoints_left, imgpoints_left, (ret_left, mtx_left, dist_left,
                                         rvecs_left, tvecs_left), shape_left = calibration_left
        objpoints_right, imgpoints_right, (ret_right, mtx_right, dist_right,
                                           rvecs_right, tvecs_right), shape_right = calibration_right
        flags = cv2.CALIB_FIX_INTRINSIC
        return cv2.stereoCalibrate(
            objpoints_left, imgpoints_left, imgpoints_right,
            mtx_left, dist_left, mtx_right, dist_right, shape_left,
            criteria=self.criteria, flags=flags)

    def rectify(self, stereo_calibration, shape):
        # Stereo rectification
        ret, mtx1, dist1, mtx2, dist2, R, T, E, F = stereo_calibration
        rectify_scale = 1  # 0 for crop, 1 for full image
        R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
            mtx1, dist1, mtx2, dist2, shape, R, T, alpha=rectify_scale)
        return R1, R2, P1, P2, Q, roi1, roi2

    def triangulate(self, keypoints1, keypoints2):
        if self.calibration_params is None or "rectification" not in self.calibration_params:
            raise ValueError(
                "Stereo rectification parameters are not available.")

        # Convert keypoints to numpy arrays
        keypoints1 = np.array(keypoints1, dtype=np.float32)  # (N, 3)
        keypoints2 = np.array(keypoints2, dtype=np.float32)  # (N, 3)
        assert keypoints1.shape == keypoints2.shape and keypoints1.shape[1] == 3

        # Only keep the keypoints where both cameras detected the point
        mask = np.logical_and(keypoints1[:, 2] > 0, keypoints2[:, 2] > 0)
        keypoints1 = keypoints1[mask]
        keypoints2 = keypoints2[mask]        

        # Triangulate the points
        rectification = self.calibration_params["rectification"]
        R1, R2, P1, P2, Q, roi1, roi2 = rectification
        points4D_hom = cv2.triangulatePoints(P1, P2, keypoints1, keypoints2)

        # Convert points from homogeneous to Euclidean coordinates
        points3D = points4D_hom[:3] / points4D_hom[3]
        points3D = points3D.T  # (N, 3) array of 3D points

        return points3D
