from .base import BaseSkeleton


class Halpe26Skeleton(BaseSkeleton):
    def __init__(self):
        joint_names = [
            "Hip",
            "RHip",
            "RKnee",
            "RAnkle",
            "RBigToe",
            "RSmallToe",
            "RHeel",
            "LHip",
            "LKnee",
            "LAnkle",
            "LBigToe",
            "LSmallToe",
            "LHeel",
            "Neck",
            "Head",
            "Nose",
            "RShoulder",
            "RElbow",
            "RWrist",
            "LShoulder",
            "LElbow",
            "LWrist",
        ]
        connections = [
            ["Hip", "RHip"],
            ["RHip", "RKnee"],
            ["RKnee", "RAnkle"],
            ["RAnkle", "RBigToe"],
            ["RAnkle", "RSmallToe"],
            ["RAnkle", "RHeel"],
            ["Hip", "LHip"],
            ["LHip", "LKnee"],
            ["LKnee", "LAnkle"],
            ["LAnkle", "LBigToe"],
            ["LAnkle", "LSmallToe"],
            ["LAnkle", "LHeel"],
            ["Hip", "Neck"],
            ["Neck", "Nose"],
            ["Nose", "Head"],
            ["Neck", "RShoulder"],
            ["RShoulder", "RElbow"],
            ["RElbow", "RWrist"],
            ["Neck", "LShoulder"],
            ["LShoulder", "LElbow"],
            ["LElbow", "LWrist"],
        ]
        super().__init__(joint_names, connections)
        self.set_feet_joints(
            [
                "RAnkle",
                "RBigToe",
                "RSmallToe",
                "RHeel",
                "LAnkle",
                "LBigToe",
                "LSmallToe",
                "LHeel",
            ]
        )
