import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from numpy import linspace

from .camera_system import CameraSystem


class CameraVisualizer:
    def __init__(
        self,
        camera_system,
        board_width=9,
        board_height=6,
        square_size=0.108,
        patternCentric=False,
    ):
        """
        Initializes the CameraSystemVisualizer.

        INPUTS:
        - camera_system: Instance of CameraSystem containing all cameras.
        - board_width: Number of squares along the width of the calibration board.
        - board_height: Number of squares along the height of the calibration board.
        - square_size: Size of each square on the calibration board.
        - patternCentric: Boolean indicating if the calibration board is static (True) or the cameras are static (False).
        """
        self.camera_system = camera_system
        self.board_width = board_width
        self.board_height = board_height
        self.square_size = square_size
        self.patternCentric = patternCentric

    def inverse_homogeneous_matrix(self, M):
        """
        Computes the inverse of a homogeneous transformation matrix.

        INPUT:
        - M: 4x4 homogeneous transformation matrix.

        OUTPUT:
        - M_inv: Inverse of the input matrix.
        """
        R = M[0:3, 0:3]
        T = M[0:3, 3]
        M_inv = np.identity(4)
        M_inv[0:3, 0:3] = R.T
        M_inv[0:3, 3] = -(R.T).dot(T)
        return M_inv

    def transform_to_matplotlib_frame(self, cMo, X, inverse=False):
        """
        Transforms a point from the camera/world frame to the matplotlib frame.

        INPUTS:
        - cMo: 4x4 transformation matrix (camera to world or vice versa).
        - X: 4xN array of points in homogeneous coordinates.
        - inverse: Boolean indicating whether to invert the transformation.

        OUTPUT:
        - Transformed points as a 4xN array.
        """
        # Rotation matrix to align with matplotlib's coordinate system
        M = np.identity(4)
        M[1, 1] = 0
        M[1, 2] = 1
        M[2, 1] = -1
        M[2, 2] = 0

        if inverse:
            return M.dot(self.inverse_homogeneous_matrix(cMo).dot(X))
        return M.dot(cMo.dot(X))

    def create_camera_model(self, camera, scale_focal=1.0, draw_frame_axis=False):
        """
        Creates a 3D model of a camera.

        INPUTS:
        - camera: Instance of Camera containing intrinsic and extrinsic parameters.
        - scale_focal: Scaling factor for the focal length.
        - draw_frame_axis: Boolean indicating whether to draw the camera's coordinate axes.

        OUTPUT:
        - List of 4xN arrays representing different parts of the camera model.
        """
        fx = camera.optim_K[0, 0]
        fy = camera.optim_K[1, 1]
        focal = 2 / (fx + fy)
        f_scale = scale_focal * focal

        # Image plane corners
        width = camera.image_size[0] / 2
        height = camera.image_size[1] / 2

        X_img_plane = np.ones((4, 5))
        X_img_plane[0:3, 0] = [-width, height, f_scale]
        X_img_plane[0:3, 1] = [width, height, f_scale]
        X_img_plane[0:3, 2] = [width, -height, f_scale]
        X_img_plane[0:3, 3] = [-width, -height, f_scale]
        X_img_plane[0:3, 4] = [-width, height, f_scale]

        # Camera pyramid (apex at camera center)
        X_pyramid = np.ones((4, 9))
        X_pyramid[0:3, 0] = [0, 0, 0]  # Camera center
        X_pyramid[0:3, 1] = [-width, height, f_scale]
        X_pyramid[0:3, 2] = [0, 0, 0]  # Camera center
        X_pyramid[0:3, 3] = [width, height, f_scale]
        X_pyramid[0:3, 4] = [0, 0, 0]  # Camera center
        X_pyramid[0:3, 5] = [width, -height, f_scale]
        X_pyramid[0:3, 6] = [0, 0, 0]  # Camera center
        X_pyramid[0:3, 7] = [-width, -height, f_scale]
        X_pyramid[0:3, 8] = [-width, height, f_scale]  # Closing the pyramid

        # Camera coordinate axes
        axis_length = scale_focal * focal * 0.5
        X_axis = np.ones((4, 2))
        X_axis[0:3, 0] = [0, 0, 0]
        X_axis[0:3, 1] = [axis_length, 0, 0]  # X-axis
        Y_axis = np.ones((4, 2))
        Y_axis[0:3, 0] = [0, 0, 0]
        Y_axis[0:3, 1] = [0, axis_length, 0]  # Y-axis
        Z_axis = np.ones((4, 2))
        Z_axis[0:3, 0] = [0, 0, 0]
        Z_axis[0:3, 1] = [0, 0, axis_length]  # Z-axis

        if draw_frame_axis:
            return [X_img_plane, X_pyramid, X_axis, Y_axis, Z_axis]
        return [X_img_plane, X_pyramid]

    def create_board_grid(self):
        """
        Creates grid lines for the calibration board.
        """
        grid_lines = []
        for i in range(self.board_width + 1):
            X_line = np.ones((4, 2))
            X_line[0:3, 0] = [i * self.square_size, 0, 0]
            X_line[0:3, 1] = [
                i * self.square_size,
                self.board_height * self.square_size,
                0,
            ]
            grid_lines.append(X_line)
        for j in range(self.board_height + 1):
            Y_line = np.ones((4, 2))
            Y_line[0:3, 0] = [0, j * self.square_size, 0]
            Y_line[0:3, 1] = [
                self.board_width * self.square_size,
                j * self.square_size,
                0,
            ]
            grid_lines.append(Y_line)
        return grid_lines

    def create_board_model(self):
        """
        Creates a 3D model of the calibration board.

        OUTPUT:
        - List of 4xN arrays representing different parts of the board model.
        """
        width = self.board_width * self.square_size
        height = self.board_height * self.square_size

        # Board corners
        X_board = np.ones((4, 5))
        X_board[0:3, 0] = [0, 0, 0]
        X_board[0:3, 1] = [width, 0, 0]
        X_board[0:3, 2] = [width, height, 0]
        X_board[0:3, 3] = [0, height, 0]
        X_board[0:3, 4] = [0, 0, 0]

        # Board coordinate axes
        axis_length = self.square_size * 2
        X_frame1 = np.ones((4, 2))
        X_frame1[0:3, 0] = [0, 0, 0]
        X_frame1[0:3, 1] = [axis_length, 0, 0]  # X-axis
        X_frame2 = np.ones((4, 2))
        X_frame2[0:3, 0] = [0, 0, 0]
        X_frame2[0:3, 1] = [0, axis_length, 0]  # Y-axis
        X_frame3 = np.ones((4, 2))
        X_frame3[0:3, 0] = [0, 0, 0]
        X_frame3[0:3, 1] = [0, 0, axis_length]  # Z-axis

        return [X_board]

    def draw_camera_boards(self, ax, extrinsics):
        """
        Draws the cameras and calibration board on the provided Axes3D object.

        INPUTS:
        - ax: Matplotlib 3D axes object.
        - extrinsics: N x 6 array where each row contains [rotation_vector, translation_vector].
        """
        grid_lines = self.create_board_grid()
        for line in grid_lines:
            X = self.transform_to_matplotlib_frame(np.eye(4), line)
            ax.plot3D(X[0, :], X[1, :], X[2, :], color="r", linewidth=0.5)

        min_values = np.zeros((3, 1))
        min_values = np.inf
        max_values = np.zeros((3, 1))
        max_values = -np.inf

        # Color mapping for multiple cameras
        num_cams = len(extrinsics)
        cm_subsection = linspace(0.0, 1.0, num_cams)
        colors = [cm.jet(x) for x in cm_subsection]

        # Draw static objects (board or cameras based on patternCentric)
        X_static = self.create_board_model()
        for i in range(len(X_static)):
            X = np.zeros(X_static[i].shape)
            for j in range(X_static[i].shape[1]):
                X[:, j] = self.transform_to_matplotlib_frame(
                    np.eye(4), X_static[i][:, j]
                )
            ax.plot3D(X[0, :], X[1, :], X[2, :], color="r")

            min_values = np.minimum(min_values, X[0:3, :].min(1).reshape(3, 1))
            max_values = np.maximum(max_values, X[0:3, :].max(1).reshape(3, 1))

        # Draw moving objects (cameras or board based on patternCentric)
        # [self.create_camera_model(cam, draw_frame_axis=True) for cam in self.camera_system.cameras]
        X_moving = X_static
        for idx in range(num_cams):
            # Extract rotation vector and translation vector
            rot_vec = extrinsics[idx, 0:3]
            trans_vec = extrinsics[idx, 3:6]

            # Convert rotation vector to rotation matrix
            R, _ = cv.Rodrigues(rot_vec)

            # Construct homogeneous transformation matrix
            cMo = np.eye(4)
            cMo[0:3, 0:3] = R
            cMo[0:3, 3] = trans_vec

            if self.patternCentric:
                X = [
                    self.transform_to_matplotlib_frame(cMo, X_cam, inverse=True)
                    for X_cam in X_moving[idx]
                ]
            else:
                X = [
                    self.transform_to_matplotlib_frame(cMo, X_cam) for X_cam in X_moving
                ]

            # Plot each part of the model
            for part in X:
                ax.plot3D(part[0, :], part[1, :], part[2, :], color=colors[idx])

                # # Define start and end points for the arrow
                # start = part[0:3, 0]
                # end = part[0:3, 1]

                # # Ensure start and end are numpy arrays
                # start = np.array(start)
                # end = np.array(end)

                # # Compute the direction vector
                # direction = end - start

                # # Plot the arrow using quiver
                # ax.quiver(
                #     start[0], start[1], start[2],
                #     direction[0], direction[1], direction[2],
                #     color=colors[idx],
                #     normalize=True
                # )

                min_values = np.minimum(min_values, part[0:3, :].min(1).reshape(3, 1))
                max_values = np.maximum(max_values, part[0:3, :].max(1).reshape(3, 1))

        return min_values, max_values

    def visualize(self):
        """
        Generates a matplotlib figure visualizing the camera system and calibration board.

        OUTPUT:
        - fig: Matplotlib figure object containing the 3D visualization.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_aspect("auto")

        # Extract extrinsics from the CameraSystem
        extrinsics = []
        for cam in self.camera_system.cameras:
            # Convert rotation matrix to rotation vector
            rot_vec, _ = cv.Rodrigues(cam.R_mat)
            rot_vec = rot_vec.flatten()
            trans_vec = cam.translation_vector.flatten()
            extrinsics.append(np.hstack((rot_vec, trans_vec)))
        extrinsics = np.array(extrinsics)

        # Draw cameras and board
        min_values, max_values = self.draw_camera_boards(ax, extrinsics)

        # Set equal aspect ratio
        self.set_axes_equal(ax)

        # Set labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Camera System Visualization")

        return fig

    def set_axes_equal(self, ax):
        """
        Sets equal scaling for all axes of a 3D plot.

        INPUT:
        - ax: Matplotlib 3D axes object.
        """
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


if __name__ == "__main__":
    cameras = CameraSystem("./data/Calib_board.toml")

    # Create a CameraSystemVisualizer instance
    visualizer = CameraVisualizer(cameras, 9, 6, 0.108)

    # Visualize the camera system
    fig = visualizer.visualize()

    plt.show()
