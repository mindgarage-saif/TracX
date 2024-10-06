from easydict import EasyDict as edict


class PipelineParams(edict):
    def __init__(self):
        self.video_files = []
        self.calibration_file = None
        self.correct_rotation = False
        self.do_synchronization = False
        self.use_marker_augmentation = False
        self.visualization_mode = "naive"
        self.visualization_args = edict()

        # self.visualization_mode = "opensim"
        # self.visualization_args = dict(
        #     with_blender=False,
        # )
