import math

import cv2
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Draw connections
connections = [
    (0, 1),
    (0, 2),
    (1, 2),
    (2, 4),
    (1, 3),
    (5, 18),
    (18, 6),
    (18, 17),
    (3, 5),
    (4, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 19),
    (19, 12),
    (11, 13),
    (12, 14),
    (13, 15),
    (14, 16),
    (15, 24),
    (24, 20),
    (24, 22),
    (16, 25),
    (25, 21),
    (25, 23),
]


def visualize3d(points3d, connections):
    """
    Visualizes 3D points and their connections using matplotlib.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Determine axes limits
    x_min = np.nanmin(points3d[:, :, 0])
    x_max = np.nanmax(points3d[:, :, 0])
    y_min = np.nanmin(points3d[:, :, 1])
    y_max = np.nanmax(points3d[:, :, 1])
    z_min = np.nanmin(points3d[:, :, 2])
    z_max = np.nanmax(points3d[:, :, 2])

    def update(frame):
        ax.clear()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # Draw connections
        for connection in connections:
            kp1, kp2 = connection
            x = [points3d[frame, kp1, 0], points3d[frame, kp2, 0]]
            y = [points3d[frame, kp1, 1], points3d[frame, kp2, 1]]
            z = [points3d[frame, kp1, 2], points3d[frame, kp2, 2]]
            ax.plot(x, y, z, color="b")

        ax.scatter(points3d[frame, :, 0], points3d[frame, :, 1], points3d[frame, :, 2])

        # Fix the scale
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)

        # Set camera position
        ax.view_init(elev=20, azim=30)

    ani = animation.FuncAnimation(fig, update, frames=points3d.shape[0], repeat=True)

    # Writer = animation.writers['ffmpeg']
    writer = animation.FFMpegWriter(fps=30, metadata=dict(artist="Me"), bitrate=1800)
    ani.save("output3d.mp4", writer=writer)
    plt.close(fig)


def visualize_grid(pose2d_views, connections, output_filename="output_grid.mp4"):
    """
    Visualizes 2D points for multiple views in a grid layout and saves to a single video.

    Args:
        pose2d_views (list): List of 2D pose arrays for each view, where each array has shape (frames, keypoints, 3).
        connections (list): List of connections between keypoints.
        output_filename (str): Output filename for the saved video.
    """
    num_views = len(pose2d_views)
    # Assuming all views have the same number of frames
    frames = pose2d_views[0].shape[0]

    video_paths = [
        "data/projects/orthosuper-patient8-trial7/videos/0.avi",
        "data/projects/orthosuper-patient8-trial7/videos/1.avi",
        "data/projects/orthosuper-patient8-trial7/videos/2.avi",
        "data/projects/orthosuper-patient8-trial7/videos/3.avi",
        "data/projects/orthosuper-patient8-trial7/videos/4.avi",
        "data/projects/orthosuper-patient8-trial7/videos/5.avi",
        "data/projects/orthosuper-patient8-trial7/videos/6.avi",
        "data/projects/orthosuper-patient8-trial7/videos/7.avi",
    ]

    # Open each video capture
    video_caps = [cv2.VideoCapture(path) for path in video_paths]
    if any(not cap.isOpened() for cap in video_caps):
        raise ValueError("One or more video files could not be opened.")

    # Determine grid size based on the number of views
    cols = math.ceil(math.sqrt(num_views))
    rows = math.ceil(num_views / cols)

    # Create figure and axes
    fig, axs = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))
    axs = axs.flatten()  # Flatten in case of single row or column

    def update(frame):
        for i, ax in enumerate(axs):
            ax.clear()
            if i >= num_views:
                ax.axis("off")
                continue

            # Read the current frame from the video capture
            ret, video_frame = video_caps[i].read()
            if not ret:
                continue

            # Convert the video frame from BGR to RGB for Matplotlib
            video_frame_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)

            # Display the video frame as background
            ax.imshow(video_frame_rgb)

            # Plot each keypoint and connection for the current view on top of the video frame
            pose2d = pose2d_views[i]
            for connection in connections:
                kp1, kp2 = connection
                x = [pose2d[frame, kp1, 0], pose2d[frame, kp2, 0]]
                y = [pose2d[frame, kp1, 1], pose2d[frame, kp2, 1]]
                ax.plot(x, y, color="b")

            ax.scatter(pose2d[frame, :, 0], pose2d[frame, :, 1], color="r")
            ax.set_title(f"View {i + 1}")
            ax.axis("off")

    # Create and save the animation
    ani = animation.FuncAnimation(fig, update, frames=frames, repeat=True)
    writer = animation.FFMpegWriter(fps=30, metadata=dict(artist="Me"), bitrate=1800)
    ani.save(output_filename, writer=writer)
    plt.close(fig)

    # Release video captures
    for cap in video_caps:
        cap.release()
