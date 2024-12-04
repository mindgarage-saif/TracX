import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from TracX.rendering.base_renderer import MotionRenderer


class StickFigureRenderer(MotionRenderer):
    """Class for rendering a stick figure skeleton."""

    def __init__(
        self,
        motion_data,
        output_path,
        monocular=False,
        elev=15,
        azim=75,
        vertical_axis="z",
    ):
        """Initialize the stick figure renderer.

        Args:
            motion_data (MotionSequence): The motion sequence to render.

        """
        super().__init__(motion_data)

        if not output_path.endswith(".mp4"):
            raise ValueError("Output file must be a .mp4 file.")

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Create a video writer
        self.writer = None
        self.fps = 25

        self.output_path = output_path
        self.output_dir = output_dir
        self.monocular = monocular
        self.elev = elev
        self.azim = azim
        self.vertical_axis = vertical_axis

        # Footstep rendering
        self.footsteps = None
        self.show_footsteps = False
        self.footstep_cfg = {
            "color": "lightgreen",
            "marker": "x",
            "alpha": 0.5,
            "zorder": 3,
        }

        # Connection rendering
        self.connection_cfg = {
            "color": "blue",
            "linewidth": 2,
            "alpha": 1.0,
            "zorder": 2,
        }

        # Joint rendering
        self.joint_cfg = {
            "color": "red",
            "marker": "o",
            "alpha": 1.0,
            "s": 5,
            "zorder": 1,
        }

    def render_frame(
        self,
        frame_idx,
        skeleton,
        metadata=None,
    ):
        """Plot and save the 3D skeleton for the given frame."""
        tmp_dir = os.path.join(self.output_dir, "tmp")
        tmp_file = os.path.join(tmp_dir, f"{frame_idx}.png")
        if os.path.exists(tmp_file):
            return

        fig = plt.figure(facecolor="lightgray", figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Plot footsteps
        if self.footsteps is not None:
            ax.scatter(
                self.footsteps[:, 0],
                self.footsteps[:, 1],
                self.footsteps[:, 2],
                **self.footstep_cfg,
            )

        # Draw connections.
        connections = skeleton.connections
        for start, end in connections:
            ax.plot(
                [start.position[0], end.position[0]],
                [start.position[1], end.position[1]],
                [start.position[2], end.position[2]],
                **self.connection_cfg,
            )

        # Draw joints.
        joints = np.array(list(skeleton.get_pose().values()))
        ax.scatter(
            joints[:, 0],
            joints[:, 1],
            joints[:, 2],
            **self.joint_cfg,
        )

        # Set axis labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # Initialize the view
        self.init_view(
            ax,
            monocular=self.monocular,
            elev=self.elev,
            azim=self.azim,
            vertical_axis=self.vertical_axis,
        )

        # Minimize whitespace
        plt.tight_layout()

        # Convert the plot to an image array
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        # Initialize the video writer if not already initialized
        if self.writer is None:
            height, width, _ = image.shape
            self.writer = cv2.VideoWriter(
                self.output_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                self.fps,
                (width, height),
            )

        # Write the image to the video
        self.writer.write(image)
        plt.close(fig)

    def render(self, fps=24):
        # Get the footsteps
        if self.show_footsteps:
            footsteps = []
            foot_joints = self.motion_data.skeleton.feet_joints
            for _, skeleton, _ in self.motion_data.iterate_frames():
                pose = skeleton.get_pose()
                foot_pose = [pose[joint] for joint in foot_joints]
                foot_heights = [position[2] for position in foot_pose]
                min_foot_joint = foot_joints[np.argmin(foot_heights)]
                footsteps.append(pose[min_foot_joint])
            self.footsteps = np.array(footsteps)

        # Render each frame
        self.fps = fps
        super().render()
