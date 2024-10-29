from .base import BaseSkeleton


class MonocularSkeleton(BaseSkeleton):
    def __init__(self):
        joint_names = [
            "Hip",
            "RHip",
            "RKnee",
            "RAnkle",
            "LHip",
            "LKnee",
            "LAnkle",
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
            ["Hip", "LHip"],
            ["LHip", "LKnee"],
            ["LKnee", "LAnkle"],
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
