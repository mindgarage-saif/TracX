from typing import Dict

from tqdm import tqdm

from ..core.motion import MotionSequence
from ..core.skeletons import BaseSkeleton


class MotionRenderer:
    """Base class for rendering a motion sequence.

    Attributes:
        motion_data (BaseSkeleton): The skeleton to render.
    """

    def __init__(self, motion_data: MotionSequence):
        self.motion_data: MotionSequence = motion_data
        self.xlimits = self.motion_data.get_xlimits()
        self.ylimits = self.motion_data.get_ylimits()
        self.zlimits = self.motion_data.get_zlimits()

    def init_view(self, ax):
        """Set the axes limits for the plot.

        Args:
            ax: The axes to set the limits for.
        """
        x_min, x_max = self.xlimits
        y_min, y_max = self.ylimits
        z_min, z_max = self.zlimits

        x_diff = x_max - x_min
        y_diff = y_max - y_min
        z_diff = z_max - z_min

        max_diff = max(x_diff, y_diff) * 0.75

        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        z_center = (z_min + z_max) / 2

        x_min = x_center - max_diff / 2
        x_max = x_center + max_diff / 2
        y_min = y_center - max_diff / 2
        y_max = y_center + max_diff / 2
        z_min = 0
        z_max = max_diff

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)

        ax.view_init(elev=15, azim=75)

    def render_frame(
        self,
        frame_idx: int,
        skeleton: BaseSkeleton,
        metadata: Dict = None,
    ):
        """Render a single frame of the motion sequence.

        Args:
            frame_idx (int): Index of the frame to render.
            skeleton (BaseSkeleton): The skeleton to render with the frame's pose.
            metadata (Dict): Additional metadata for the frame.
        """
        raise NotImplementedError

    def render(self):
        """Render the motion sequence."""
        for frame_idx, skeleton, metadata in tqdm(
            self.motion_data.iterate_frames(),
            total=len(self.motion_data),
            desc="Rendering motion",
        ):
            self.render_frame(frame_idx, skeleton, metadata)
