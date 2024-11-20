# Triangulate 3D points
def triangulate(pose2d, projection_matrices, threshold=0.1):
    """
    Triangulates 3D points from multiple 2D poses and projection matrices.
    Uses all available camera views to compute the most accurate 3D point.

    Args:
        pose2d (np.ndarray): 2D poses for each camera view. Shape: (views, frames, keypoints, 3)
                             where 3 represents (x, y, confidence).
        projection_matrices (np.ndarray): Projection matrices for each camera view. Shape: (views, 3, 4).
        threshold (float): Minimum confidence threshold to include a keypoint in triangulation.

    Returns:
        np.ndarray: 3D points for each keypoint in each frame. Shape: (frames, keypoints, 3).
    """
    views, frames, keypoints, _ = pose2d.shape
    points3d_all_frames = []

    # Loop through each frame
    for frame_idx in range(frames):
        points3d_frame = []

        # Loop through each keypoint
        for kp_idx in range(keypoints):
            A = []  # System matrix for triangulation

            # Gather equations from each camera view where confidence > threshold
            for view_idx in range(views):
                x, y, confidence = pose2d[view_idx, frame_idx, kp_idx]

                # Debugging: Print to check coordinates and confidence
                if frame_idx == 0 and kp_idx == 0:
                    print(
                        f"View {view_idx}, Frame {frame_idx}, Keypoint {kp_idx}: x={x}, y={y}, confidence={confidence}"
                    )

                if confidence < threshold:
                    continue  # Skip low-confidence points

                P = projection_matrices[view_idx]

                # Construct the equations for triangulation based on projection matrix and 2D points
                A.append((x * P[2] - P[0]))
                A.append((y * P[2] - P[1]))

            # If fewer than two views are available, skip this keypoint
            if len(A) < 2:
                points3d_frame.append([np.nan, np.nan, np.nan])
                continue

            # Debugging: Check condition of matrix A
            A = np.array(A)
            if np.linalg.matrix_rank(A) < 3:
                print(
                    f"Low rank matrix A for frame {frame_idx}, keypoint {kp_idx}: insufficient for triangulation"
                )
                points3d_frame.append([np.nan, np.nan, np.nan])
                continue

            # Solve the triangulation equation A * X = 0 using SVD
            _, _, Vt = svd(A)
            X = Vt[-1]

            # Check if X has four elements before attempting normalization
            if X.shape[0] == 4 and X[3] != 0:
                X = X / X[3]  # Normalize to homogeneous coordinates
                points3d_frame.append(X[:3])  # Append the 3D point
            else:
                # In case triangulation fails
                points3d_frame.append([np.nan, np.nan, np.nan])

        # Append all 3D keypoints for the current frame
        points3d_all_frames.append(points3d_frame)

    # Convert list of frames to a NumPy array with shape (frames, keypoints, 3)
    return np.array(points3d_all_frames)


# Triangulate 3D points
points3d = triangulate(pose2d, projection_matrices)
print(points3d.shape)  # (26, 3)


# Visualize 3D points
print(points3d.shape)
visualize3d(points3d, connections)
