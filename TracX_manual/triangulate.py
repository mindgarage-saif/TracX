import numpy as np

from .calibration import load_camera_calibration


def euclidean_to_homogeneous(points):
    """Converts euclidean points to homogeneous

    Args:
        points numpy array of shape (N, M): N euclidean points of dimension M

    Returns:
        numpy array of shape (N, M + 1): homogeneous points
    """
    return np.hstack([points, np.ones((len(points), 1))])


def homogeneous_to_euclidean(points):
    """Converts homogeneous points to euclidean

    Args:
        points numpy array of shape (N, M + 1): N homogeneous points of dimension M

    Returns:
        numpy array of shape (N, M): euclidean points
    """
    return (points.T[:-1] / points.T[-1]).T


def project_3d_points_to_image_plane(
    proj_matrix, points_3d, convert_back_to_euclidean=True
):
    """Project 3D points to image plane not taking into account distortion
    Args:
        proj_matrix numpy array of shape (3, 4): projection matrix
        points_3d numpy array of shape (N, 3): 3D points
        convert_back_to_euclidean bool: if True, then resulting points will be converted to euclidean coordinates
                                        NOTE: division by zero can be here if z = 0
    Returns:
        numpy array of shape (N, 2): 3D points projected to image plane
    """
    result = euclidean_to_homogeneous(points_3d) @ proj_matrix.T  # x = P * X
    if convert_back_to_euclidean:
        result = homogeneous_to_euclidean(result)
    return result


def triangulate_points(proj_matrices, points, confidences=None):
    """Similar as triangulate_point_from_multiple_views_linear() but for PyTorch.
    For more information see its documentation.
    Args:
        proj_matricies numpy array of shape (N, 3, 4): sequence of projection matricies (3x4)
        points numpy array of of shape (N, 2): sequence of points' coordinates
        confidences None or numpy array of shape (N,): confidences of points [0.0, 1.0].
                                                        If None, all confidences are supposed to be 1.0
    Returns:
        point_3d numpy array of shape (3,): triangulated point
    """
    assert len(proj_matrices) == len(points)

    n_views = len(proj_matrices)

    # Set default confidences if None
    if confidences is None:
        confidences = np.ones(n_views, dtype=np.float32)

    # Create matrix A
    A = np.zeros((2 * n_views, 4))
    for j in range(n_views):
        P = proj_matrices[j]  # P = K[R|t] of shape 3x4
        x, y = points[j]
        c = confidences[j]

        # Skip points with low confidence
        if c < 0.5:
            print("Skipping point with low confidence")
            continue

        A[2 * j] = x * P[2, :] - P[0, :]
        A[2 * j + 1] = y * P[2, :] - P[1, :]

    # Perform SVD on A
    _, _, vh = np.linalg.svd(A, full_matrices=False)

    # The solution is the last row of vh (smallest singular value)
    point_3d_homo = vh[-1, :]

    return homogeneous_to_euclidean(point_3d_homo)


def triangulate_points_batch(proj_matrices_batch, points_batch, confidences_batch=None):
    batch_size, n_views, n_joints = points_batch.shape[:3]
    point_3d_batch = np.zeros((batch_size, n_joints, 3), dtype=np.float32)

    for batch_i in range(batch_size):
        for joint_i in range(n_joints):
            points = points_batch[batch_i, :, joint_i, :]

            confidences = (
                confidences_batch[batch_i, :, joint_i]
                if confidences_batch is not None
                else None
            )
            point_3d = triangulate_points(
                proj_matrices_batch, points, confidences=confidences
            )
            point_3d_batch[batch_i, joint_i] = point_3d

    return point_3d_batch


def calc_reprojection_error_matrix(keypoints_3d, keypoints_2d_list, proj_matricies):
    """
    Calculate the reprojection error matrix for a set of 3D keypoints and their
    corresponding 2D projections.

        Args:
        keypoints_3d (torch.Tensor): A tensor of shape (N, 3) representing the 3D keypoints.
        keypoints_2d_list (list of torch.Tensor): A list of tensors, each of shape (N, 2),
            representing the 2D keypoints for each view.
        proj_matricies (list of np.ndarray): A list of projection matrices, each of shape
            (3, 4), corresponding to each view.
    Returns:
        torch.Tensor: A tensor of shape (N, M) where N is the number of keypoints and M is
            the number of views, representing the reprojection error for each keypoint in
            each view.
    """
    reprojection_error_matrix = []
    for keypoints_2d, proj_matrix in zip(keypoints_2d_list, proj_matricies):
        keypoints_2d_projected = project_3d_points_to_image_plane(
            proj_matrix, keypoints_3d
        )
        reprojection_error = (
            1
            / 2
            * np.sqrt(np.sum((keypoints_2d - keypoints_2d_projected) ** 2, axis=1))
        )
        reprojection_error_matrix.append(reprojection_error)

    return np.vstack(reprojection_error_matrix).T


def main():
    # Load camera calibration data
    proj_matrices = []
    for i in range(8):
        P = load_camera_calibration(
            f"data/projects/orthosuper-patient8-trial7/calibration/matrices/{i}.txt"
        )["P"]
        proj_matrices.append(P)
    proj_matrices = np.array(proj_matrices)
    print("Projection Matrices:", proj_matrices.shape)  # shape: (Views, 3, 4)

    # Load 2D pose data
    pose2d = np.load(
        "pose2d.npy"
    )  # shape: (Views, Frames, Joints, 3) where 3 = x, y, confidence
    pose2d = pose2d.transpose(1, 0, 2, 3)  # shape: (Frames, Views, Joints, 3)
    print("2D Pose Data:", pose2d.shape)  # shape: (Frames, Views, Joints, 3)

    # Triangulate 3D keypoints
    keypoints_3d = triangulate_points_batch(
        proj_matrices, pose2d[:, :, :, :2], pose2d[:, :, :, 2]
    )
    print("3D Keypoints:", keypoints_3d.shape)  # shape: (Frames, Joints, 3)
    print("3D Keypoints:", keypoints_3d[0])  # shape: (Frames, Joints, 3)
    visualize3d(keypoints_3d, connections)

    # Calculate reprojection error
    reprojection_error_matrices = []
    for frame_idx in range(keypoints_3d.shape[0]):
        reprojection_error_matrix = calc_reprojection_error_matrix(
            keypoints_3d[frame_idx], pose2d[frame_idx, :, :, :2], proj_matrices
        )
        reprojection_error_matrices.append(reprojection_error_matrix)
    reprojection_error_matrices = np.stack(reprojection_error_matrices)
    print(
        "Reprojection Error Matrices:", reprojection_error_matrices.shape
    )  # shape: (Frames, Joints, Views)

    # Average reprojection error for each joint
    avg_reprojection_error = np.mean(reprojection_error_matrices, axis=2)
    print(
        "Average Reprojection Error:", avg_reprojection_error.shape
    )  # shape: (Frames, Joints)

    print(
        "RMSE:", np.sqrt(np.mean(avg_reprojection_error**2, axis=0))
    )  # shape: (Joints)


if __name__ == "__main__":
    main()
