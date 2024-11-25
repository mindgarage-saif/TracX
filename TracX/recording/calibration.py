import os

import cv2
import numpy as np


class Calibration:
    def __init__(
        self,
        checkerboard_size=(9, 14),
        world_scaling=20,  # mm
    ):
        # Checkerboard settings
        self.rows = checkerboard_size[0]  # Number of rows
        self.columns = checkerboard_size[1]  # Number of columns
        self.world_scaling = world_scaling  # Checkerboard square size in mm

        # Criteria used by checkerboard pattern detector.
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.calibration_params = None

    def calibrate_single(
        self,
        images,
        name="camera",
        conv_size=(11, 11),  # Convolution size for corner detection
    ):
        rows = self.rows
        columns = self.columns
        world_scaling = self.world_scaling
        criteria = self.criteria

        # Create a 3D grid of points in real-world space
        objp = np.zeros((rows * columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        objp = world_scaling * objp

        # Frame dimensions
        width = images[0].shape[1]
        height = images[0].shape[0]

        # Lists to store object points and image points from all the images
        objpoints = []  # 3D points in real-world space
        imgpoints = []  # 2D points in the image plane

        save_dir = f"calibration/{name}"
        os.makedirs(save_dir, exist_ok=True)
        for frame in images:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Find the chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)

            if ret:
                # Refine the corners for better accuracy
                corners = cv2.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)

                objpoints.append(objp)
                imgpoints.append(corners)

        # Check if any corners were detected
        if len(objpoints) == 0:
            return None

        # Calibrate the camera
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            (width, height),
            None,
            None,
        )

        # Print calibration results
        print(f"Calibration results for {name} camera:")
        print("RMSE:", ret)
        print("Camera matrix:")
        print(mtx)
        print("Distortion coefficients:")
        print(dist)
        print("Per frame rotations:")
        print(rvecs)
        print("Per frame translations:")
        print(tvecs)

        if ret > 1:
            print("High RMSE. Calibration for camera", name, "may not be accurate.")

        return objpoints, imgpoints, (ret, mtx, dist, rvecs, tvecs), (width, height)

    def rectify(self, stereo_calibration, shape):
        # Stereo rectification
        ret, mtx1, dist1, mtx2, dist2, R, T, E, F = stereo_calibration
        rectify_scale = 1  # 0 for crop, 1 for full image
        R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
            mtx1,
            dist1,
            mtx2,
            dist2,
            shape,
            R,
            T,
            alpha=rectify_scale,
        )
        return R1, R2, P1, P2, Q, roi1, roi2

    def calibrate(self, images):
        c1_images = [i[0] for i in images]
        c2_images = [i[1] for i in images]
        assert len(c1_images) == len(c2_images) and len(c2_images) > 0
        print("Calibrating with", len(c2_images), "frames")

        calibration1 = self.calibrate_single(c1_images, "camera1")
        calibration2 = self.calibrate_single(c2_images, "camera2")

        failure1 = calibration1 is None
        failure2 = calibration2 is None
        print("Calibration status: camera1 =", not failure1, "camera2 =", not failure2)
        if failure1 or failure2:
            raise ValueError("Calibration failed for one or both cameras.")

        # Stereo calibration
        objpoints1, imgpoints1, (_, mtx1, dist1, _, _), shape = calibration1
        objpoints2, imgpoints2, (_, mtx2, dist2, _, _), _ = calibration2
        flags = cv2.CALIB_FIX_INTRINSIC
        stereo_calibration = cv2.stereoCalibrate(
            objpoints1,
            imgpoints1,
            imgpoints2,
            mtx1,
            dist1,
            mtx2,
            dist2,
            shape,
            criteria=self.criteria,
            flags=flags,
        )

        # Stereo rectification
        ret, CM1, dist1, CM2, dist2, R, T, E, F = stereo_calibration
        rectification = self.rectify(stereo_calibration, shape)

        # Save the calibration parameters
        self.calibration_params = {
            "left": calibration_left,
            "right": calibration_right,
            "stereo": stereo_calibration,
            "rectification": rectification,
        }

    def triangulate(self, keypoints1, keypoints2):
        if (
            self.calibration_params is None
            or "rectification" not in self.calibration_params
        ):
            raise ValueError("Stereo rectification parameters are not available.")

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
        return points3D.T  # (N, 3) array of 3D points
