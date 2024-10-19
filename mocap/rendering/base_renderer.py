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

    def get_difference(self,minimum,maximum):
        # minimum can be negative and maximum can also be negative
        # if minimum is negative and maximum is positive, then the difference is maximum

        if minimum < 0 and maximum < 0:
            return abs(minimum) - abs(maximum)
        elif minimum < 0 and maximum > 0:
            return abs(minimum) + maximum
        else:
            return maximum - minimum

    def init_view(self, ax, **kwargs):
        """Set the axes limits for the plot.

        Args:
            ax: The axes to set the limits for.
        """
        x_min, x_max = self.xlimits
        y_min, y_max = self.ylimits
        z_min, z_max = self.zlimits

        x_diff = self.get_difference(x_min,x_max)
        y_diff = self.get_difference(y_min,y_max)
        z_diff = self.get_difference(z_min,z_max)
        if "monocular" in kwargs:
            max_diff = max(x_diff, y_diff,z_diff) * 0.75
        else:
            max_diff = max(x_diff, y_diff) * 0.75
        

        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        z_center = (z_min + z_max) / 2

        x_min = x_center - max_diff / 2
        x_max = x_center + max_diff / 2
        y_min = y_center - max_diff / 2
        y_max = y_center + max_diff / 2
        if "monocular" in kwargs:
            z_min = z_center - max_diff / 2
            z_max = z_center + max_diff / 2
        else:
            z_min = 0
            z_max = max_diff

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)
        elev = kwargs.get("elev", 15)
        azim = kwargs.get("azim", 75)
        vertical_axis = kwargs.get("vertical_axis", "z")
        ax.view_init(elev=elev, azim=azim,vertical_axis=vertical_axis)

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
        print("Rendering frame2")
        raise NotImplementedError

    def render(self):
        """Render the motion sequence."""
        for frame_idx, skeleton, metadata in tqdm(
            self.motion_data.iterate_frames(),
            total=len(self.motion_data),
            desc="Rendering motion",
        ):
            self.render_frame(frame_idx, skeleton, metadata)
