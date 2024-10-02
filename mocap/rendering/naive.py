import os
import shutil

import matplotlib.pyplot as plt
import numpy as np

from .utils import df_from_trc, export_video


def set_axes_equal(ax, limits):
    """Set 3D plot axes to have equal scale."""
    xs_min, xs_max, ys_min, ys_max, zs_min, zs_max = limits
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)


def fit_ground_plane(ground_points):
    """
    Fit a plane through the ground points using least squares, assuming XZ is the ground and Y is the vertical axis.
    Args:
        ground_points: List of ground points (x, y, z) where y is the vertical (up) axis.
    Returns:
        Plane coefficients (a, b, d) for the equation y = ax + bz + d
    """
    # Ground points as numpy array
    ground_points = np.array(ground_points)

    # Extract the coordinates (x, z are independent variables, y is dependent)
    xs, zs, ys = ground_points[:, 0], ground_points[:, 2], ground_points[:, 1]

    # Fit a plane using the least squares method to find a, b, and d in the equation y = ax + bz + d
    A = np.c_[xs, zs, np.ones(ground_points.shape[0])]
    C, _, _, _ = np.linalg.lstsq(A, ys, rcond=None)  # Plane coefficients
    return C  # C contains [a, b, d], where the plane equation is y = ax + bz + d


def create_naive_vis(
    xs,
    ys,
    zs,
    limits,
    connections,
    frame_idx,
    output_dir,
    ground_points=None,
    ground_plane=None,
):
    """
    Plot and save the 3D skeleton for the given frame.
    """
    fig = plt.figure(figsize=(10, 10), facecolor="lightgray")
    ax = fig.add_subplot(111, projection="3d")

    sky_blue = (0.01, 0.80, 0.99, 1.0)
    brick_red = (0.56, 0.08, 0.08, 1.0)
    mortar_gray = (0.95, 0.87, 0.82, 0.2)

    # Plot all ground points
    min_foot_height = min([foot[1] for foot in ground_points])
    for foot in ground_points:
        ax.scatter(foot[2], foot[0], foot[1], color=brick_red, marker="x", alpha=0.5)

    ys = ys - min_foot_height  # Translate the Y coordinates to the minimum foot height

    # Plot ground plane if available
    if ground_plane is not None:
        # Create a meshgrid for the ground plane
        x = np.linspace(limits[0], limits[1], 10)
        z = np.linspace(limits[4], limits[5], 10)
        x, z = np.meshgrid(x, z)
        a, b, d = ground_plane
        y = a * x + b * z + d

        # Translate the ground plane to the minimum foot height
        y = y - min_foot_height - 3.5
        x *= 1.2
        x = x - 8
        z *= 5
        z = z - 2.5

        # Compute normal vector
        normal = np.array([a, -1, b])
        normal = normal / np.linalg.norm(normal)

        # Plot the ground plane
        ax.plot_surface(
            z,
            x,
            y,
            alpha=0.2,
            linewidth=0,
            antialiased=False,
            color="white",
            edgecolor="lightgray",
        )

        # Use normal vector to get camera elevation and azimuth
        elevation = 15  # 90 - np.degrees(np.arcsin(normal[1]))  # Elevation based on the Y component of the normal
        azimuth = 79  # np.degrees(np.arctan2(normal[2], normal[0]))  # Azimuth based on X and Z components
    else:
        elevation = 15
        azimuth = 79

    # Draw connections (make sure they appear above the ground plane)
    for connection in connections:
        ax.plot(
            [zs[connection[0]], zs[connection[1]]],
            [xs[connection[0]], xs[connection[1]]],
            [ys[connection[0]], ys[connection[1]]],
            color=connection[2],
            linewidth=3,
            zorder=1,
        )

    ax.scatter(zs, xs, ys, color=sky_blue, marker="o")

    # Set axis labels
    ax.set_xlabel("Z")
    ax.set_ylabel("X")
    ax.set_zlabel("Y")

    # no grid
    ax.grid(False)

    # hide axes planes
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)

    # hide axes
    ax.set_axis_off()

    # Set axis limits
    set_axes_equal(ax, limits)

    # Set grid color
    # ax.xaxis.pane.set_edgecolor(mortar_gray)
    # ax.yaxis.pane.set_edgecolor(mortar_gray)
    # ax.zaxis.pane.set_edgecolor(mortar_gray)
    # ax.xaxis._axinfo["grid"]['color'] = mortar_gray
    # ax.yaxis._axinfo["grid"]['color'] = mortar_gray
    # ax.zaxis._axinfo["grid"]['color'] = mortar_gray
    # ax.xaxis.pane.set_facecolor(brick_red)
    # ax.yaxis.pane.set_facecolor(brick_red)
    # ax.zaxis.pane.set_facecolor(brick_red)

    ax.view_init(elev=elevation, azim=azimuth)

    # Minimize whitespace
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(output_dir, f"{frame_idx}.png"))
    plt.close()


def export_naive_vis(motion_file, save_path):
    if not motion_file.endswith(".trc"):
        raise ValueError("Input file must be a .trc file.")

    if not save_path.endswith(".mp4"):
        raise ValueError("Output file must be a .mp4 file.")

    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    header, data = df_from_trc(motion_file)
    bodyparts = np.array([d[:-2] for d in data.columns[2::3]])

    xs, ys, zs = None, None, None
    color_left = "lightcoral"
    color_right = "lightgreen"
    color_mid = "lightblue"
    connections = [
        [0, 1, color_mid],
        [1, 2, color_right],
        [2, 3, color_right],
        [3, 4, color_right],
        [3, 5, color_right],
        [3, 6, color_right],
        [0, 7, color_mid],
        [7, 8, color_left],
        [8, 9, color_left],
        [9, 10, color_left],
        [9, 11, color_left],
        [9, 12, color_left],
        [0, 13, color_mid],
        [13, 15, color_mid],
        [15, 14, color_mid],
        [13, 16, color_right],
        [16, 17, color_right],
        [17, 18, color_right],
        [13, 19, color_left],
        [19, 20, color_left],
        [20, 21, color_left],
    ]

    tmp_dir = os.path.join(save_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # Store ground points
    ground_points = []

    # Aggregate data for each frame
    for bp in bodyparts:
        bp_X = bp + "_X"
        bp_Y = bp + "_Y"
        bp_Z = bp + "_Z"
        if xs is None:
            xs = np.array(data[bp_X]).reshape(-1, 1)
            ys = np.array(data[bp_Y]).reshape(-1, 1)
            zs = np.array(data[bp_Z]).reshape(-1, 1)
        else:
            xs = np.concatenate((xs, np.array(data[bp_X]).reshape(-1, 1)), axis=1)
            ys = np.concatenate((ys, np.array(data[bp_Y]).reshape(-1, 1)), axis=1)
            zs = np.concatenate((zs, np.array(data[bp_Z]).reshape(-1, 1)), axis=1)

    # Pre-compute axis limits
    xs_min, xs_max = xs.min(), xs.max()
    ys_min, ys_max = ys.min(), ys.max()
    zs_min, zs_max = zs.min(), zs.max()
    limits = xs_min, xs_max, ys_min, ys_max, zs_min, zs_max

    # Compute ground points
    foot_indices = [
        4,
        5,
        6,
        10,
        11,
        12,
    ]  # Indices of the foot points in the data (e.g., toes and heels)

    for i in range(xs.shape[0]):
        foot_heights = ys[i, foot_indices]  # Get foot z-coordinates for current frame
        min_foot_idx = foot_indices[
            np.argmin(foot_heights)
        ]  # Index of the foot with minimum height
        ground_points.append(
            [xs[i, min_foot_idx], ys[i, min_foot_idx], zs[i, min_foot_idx]]
        )

    # Fit the ground plane for the first few frames and then use the same
    ground_plane = fit_ground_plane(ground_points)

    for i in range(xs.shape[0]):
        create_naive_vis(
            xs[i],
            ys[i],
            zs[i],
            limits,
            connections,
            i,
            tmp_dir,
            ground_points,
            ground_plane,
        )

    # Create video
    export_video(tmp_dir, save_path)

    # Clean up temporary images
    shutil.rmtree(tmp_dir)
