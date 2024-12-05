# Copyright (C) 2024 Max Planck Institute for Intelligent Systems, Marilyn Keller, marilyn.keller@tuebingen.mpg.de

import argparse
import os
from typing import Optional

from aitviewer.renderables.markers import Markers
from aitviewer.renderables.osim import OSIMSequence
from aitviewer.utils.vtp_to_ply import convert_meshes
from aitviewer.viewer import Viewer


def render(
    osim: Optional[str] = None,
    mot: Optional[str] = None,
    fps: Optional[int] = None,
    color_parts: bool = False,
    color_markers: bool = False,
    mocap: Optional[str] = None,
    joints: bool = False,
):
    """
    Load an OpenSim model and a motion file and display it in the viewer.
    Args:
        osim (str, optional): Path to the osim file. If no file is specified, the default Rajagopal gait model will be loaded from nimble. Defaults to None.
        mot (str, optional): Path to the motion file. Defaults to None.
        fps (int, optional): Generating the meshes for all the frames can take a long time and a lot of memory. Use a low fps to avoid this problem. Defaults to 30.
        color_parts (bool, optional): Color the skeleton by parts, as defined in the .osim file. Defaults to False.
        color_markers (bool, optional): Each marker is attached to a skeleton part. This option colors the markers to match the parent part color. Defaults to False.
        mocap (str, optional): If a Mocap file is specified, display the markers mocap with their labels. For now, only the .c3d format is supported. Defaults to None.
        joints (bool, optional): Show model joints as spheres. Defaults to False.
    """

    if osim is not None:
        # Check that a folder named Geometry exists in the same folder as the osim file.
        osim_dir = os.path.dirname(osim)
        geom_dir = os.path.join(osim_dir, "Geometry")
        if not os.path.exists(geom_dir):
            print(
                "Geometry folder does not exist in the same folder as the osim file. Please add a Geometry folder containing the skeleton .vtp, .obj or .ply file in the same folder as the provided .osim. "
            )
            exit(1)

        # Check that the Geometry folder contains at least a file of type .ply
        ply_files = [f for f in os.listdir(geom_dir) if f.endswith(".ply")]
        if len(ply_files) == 0:
            print("Geometry folder does not contain any .ply files.")
            print(
                "The provided folder meshes will be converted to .ply. Press a key to continue or CTRL-C to abort."
            )

            # Convert the provided meshes to .ply
            convert_meshes(geom_dir, geom_dir)

    if mot is None:
        osim_seq = OSIMSequence.a_pose(
            osim,
            name="OpenSim template",
            show_joint_angles=joints,
            color_skeleton_per_part=color_parts,
            color_markers_per_part=color_markers,
        )

    else:
        osim_seq = OSIMSequence.from_files(
            osim,
            mot,
            show_joint_angles=joints,
            color_skeleton_per_part=color_parts,
            color_markers_per_part=color_markers,
            fps_out=fps,
        )

    v = Viewer()
    v.scene.add(osim_seq)

    v.lock_to_node(osim_seq, (5, 2, 0), smooth_sigma=5.0)

    if mocap is not None:
        # check that the mocap file is in .c3d format
        assert mocap.endswith(".c3d"), "Mocap file must be in .c3d format."
        marker_seq = Markers.from_c3d(
            mocap, fps_out=fps, color=[0, 255, 0, 255]
        )
        v.scene.add(marker_seq)

    if fps is not None:
        v.playback_fps = fps

    v.run_animations = True

    v.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load an OpenSim model and a motion file and display it in the viewer."
    )

    parser.add_argument(
        "--osim",
        type=str,
        help="Path to the osim file. If no file is specified, the default Rajagopal gait model will be loaded from nimble",
        default=None,
    )
    parser.add_argument("--mot", type=str, help="Path to the motion file", default=None)
    parser.add_argument(
        "--fps",
        type=int,
        default=None,
        help="Generating the meshes for all the frames can take a long time and a lot of memory. Use a low fps to avoid this problem.",
    )

    parser.add_argument(
        "--color_parts",
        action="store_true",
        help="Color the skeleton by parts, as defined in the .osim file.",
    )
    parser.add_argument(
        "--color_markers",
        action="store_true",
        help="Each marker is attached to a skeleton part. This option colors the markers to match the parent part color.",
    )
    parser.add_argument(
        "--mocap",
        type=str,
        help="If a Mocap file is specified, display the markers mocap with their labels. For now, only the .c3d format is supported.",
    )
    parser.add_argument(
        "--joints", action="store_true", help="Show model joints as spheres."
    )

    args = parser.parse_args()

    render(
        osim=args.osim,
        mot=args.mot,
        fps=args.fps,
        color_parts=args.color_parts,
        color_markers=args.color_markers,
        mocap=args.mocap,
        joints=args.joints,
    )
