import logging
import os
from distutils.dir_util import copy_tree

import cv2
from Pose2Sim.Utilities import bodykin_from_mot_osim

from mocap.constants import (
    OPENSIM_DIR,
)
from mocap.core import Experiment, MotionSequence
from mocap.rendering import StickFigureRenderer, create_osim_models

from .base_task import BaseTask


class ExperimentVisualizer:
    """"""

    def __init__(self, experiment: Experiment):
        self.experiment = experiment
        self.output_dir = experiment.output_dir

    def _visualize_naive(self, motion_file):
        # Create a side-by-side visualization using OpenCV
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if os.path.exists(animation_file):
            return animation_file

        # Find FPS of the first camera video
        video_file = self.experiment.videos[0]
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        skeleton = self.experiment.read_skeleton()

        # Create the visualization
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if self.monocular:
            logging.info("Rendering monocular motion sequence...")
            motion_data = MotionSequence.from_monocular_json(motion_file, fps)
            renderer = StickFigureRenderer(
                motion_data,
                animation_file,
                monocular=True,
                elev=-165,
                azim=155,
                vertical_axis="y",
            )
        else:
            logging.info("Rendering multiview motion sequence...")
            motion_data = MotionSequence.from_pose2sim_trc(motion_file, skeleton)
            renderer = StickFigureRenderer(motion_data, animation_file)
        renderer.render(fps=fps)

        return animation_file

    def _visualize_opensim(self, motion_file, with_blender=False):
        copy_tree(
            os.path.join(OPENSIM_DIR, "..", "Geometry"),
            os.path.join(self.output_dir, "Geometry"),
        )
        output, mot, scaled_model = create_osim_models(
            trc=motion_file,
            experiment_dir=self.experiment.path,
        )

        if with_blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(
                mot,
                scaled_model,
                os.path.join(output, "bodykin.csv"),
            )

        return output, mot, scaled_model

    def visualize(self, mode="naive", **kwargs):
        """Visualize the results of the experiment.

        Args:
            mode (str): The visualization mode. Supported modes include ['naive', 'mesh', mixamo', 'opensim'].
            **kwargs: Additional keyword arguments to pass to the visualization function for the selected mode.
                      See the documentation of the corresponding visualization function for more details.

        """
        motion_file = self.experiment.get_motion_file()
        if motion_file is None:
            raise ValueError(
                "Call the .process() method first before visualizing the results.",
            )

        # Check the visualization mode
        supported_modes = ["naive", "mesh", "mixamo", "opensim"]
        if mode == "naive":
            return self._visualize_naive(motion_file, **kwargs)
        if mode == "opensim":
            return self._visualize_opensim(motion_file, **kwargs)
        raise ValueError(
            f"Unsupported visualization mode '{mode}'. Use one of {supported_modes}",
        )


class VisualizeMotionTask(BaseTask):
    """Task for visualizing estimated motion."""

    def __init__(self, config):
        super().__init__(config)

    def _execute_impl(self):
        # Read task configuration
        experiment_name = self.experiment

        if experiment_name is None:
            raise ValueError("Experiment name is required for visualization")

        logging.info("Visualizing 3D motion...")
        experiment = Experiment(experiment_name, create=False)
        visualizer = ExperimentVisualizer(experiment)
        visualization_mode = experiment.cfg.get("visualizer", {}).get("mode", "naive")
        if visualization_mode == "naive":
            logging.info("Visualizing motion using naive method...")
            overwrite = experiment.cfg.get("visualizer", {}).get("overwrite", True)
            result = visualizer.visualize(
                mode=visualization_mode,
                overwrite=overwrite,
            )
        elif visualization_mode == "opensim":
            logging.info("Visualizing motion using OpenSim...")
            with_blender = (
                experiment.cfg.get("visualizer", {})
                .get("opensim", {})
                .get("with_blender", False)
            )
            result = visualizer.visualize(
                mode=visualization_mode,
                with_blender=with_blender,
            )
        else:
            raise ValueError(f"Unsupported visualization mode '{visualization_mode}'")

        logging.info("Pipeline execution complete.")
        return result
