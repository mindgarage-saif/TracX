import argparse

from TracX.core import MotionSequence
from TracX.rendering.stick import StickFigureRenderer


def visualize_motion(motion_file, output_path):
    # Check if the output file is an MP4 file
    if not output_path.endswith(".mp4"):
        raise ValueError("Output file must be a .mp4 file.")

    # Load the motion data
    if motion_file.endswith(".json"):
        motion_data = MotionSequence.from_theia_json(motion_file)
    elif motion_file.endswith(".trc"):
        motion_data = MotionSequence.from_pose2sim_trc(motion_file)
    else:
        raise ValueError("Unsupported file format")

    # Create the renderer
    renderer = StickFigureRenderer(motion_data, output_path)

    # Render the animation
    renderer.render()


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize a 3D motion sequence.")
    parser.add_argument(
        "motion_file",
        type=str,
        help="The path to the 3D motion file (Theia JSON or Pose2Sim TRC).",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="The path to the output MP4 file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    visualize_motion(args.motion_file, args.output_path)


if __name__ == "__main__":
    main()
