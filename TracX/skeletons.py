from anytree import Node

from Pose2Sim.skeletons import *

"""BODY_43 (full-body without hands like HALPE_26 and 17 spine joints)"""
BODY_43 = Node(
    "Hip",
    id=19,
    children=[
        Node(
            "RHip",
            id=12,
            children=[
                Node(
                    "RKnee",
                    id=14,
                    children=[
                        Node(
                            "RAnkle",
                            id=16,
                            children=[
                                Node(
                                    "RBigToe",
                                    id=21,
                                    children=[
                                        Node("RSmallToe", id=23),
                                    ],
                                ),
                                Node("RHeel", id=25),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Node(
            "LHip",
            id=11,
            children=[
                Node(
                    "LKnee",
                    id=13,
                    children=[
                        Node(
                            "LAnkle",
                            id=15,
                            children=[
                                Node(
                                    "LBigToe",
                                    id=20,
                                    children=[
                                        Node("LSmallToe", id=22),
                                    ],
                                ),
                                Node("LHeel", id=24),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Node(
            "Neck",
            id=18,
            children=[
                Node(
                    "Head",
                    id=17,
                    children=[
                        Node("Nose", id=0),
                    ],
                ),
                Node(
                    "RShoulder",
                    id=6,
                    children=[
                        Node(
                            "RElbow",
                            id=8,
                            children=[
                                Node("RWrist", id=10),
                            ],
                        ),
                    ],
                ),
                Node(
                    "LShoulder",
                    id=5,
                    children=[
                        Node(
                            "LElbow",
                            id=7,
                            children=[
                                Node("LWrist", id=9),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Node(
            "Lumbar5",
            id=26,
            children=[
                Node(
                    "Lumbar4",
                    id=27,
                    children=[
                        Node(
                            "Lumbar3",
                            id=28,
                            children=[
                                Node(
                                    "Lumbar2",
                                    id=29,
                                    children=[
                                        Node(
                                            "Lumbar1",
                                            id=30,
                                            children=[
                                                Node(
                                                    "Thoracic12",
                                                    id=31,
                                                    children=[
                                                        Node(
                                                            "Thoracic11",
                                                            id=32,
                                                            children=[
                                                                Node(
                                                                    "Thoracic10",
                                                                    id=33,
                                                                    children=[
                                                                        Node(
                                                                            "Thoracic9",
                                                                            id=34,
                                                                            children=[
                                                                                Node(
                                                                                    "Thoracic8",
                                                                                    id=35,
                                                                                    children=[
                                                                                        Node(
                                                                                            "Thoracic7",
                                                                                            id=36,
                                                                                            children=[
                                                                                                Node(
                                                                                                    "Thoracic6",
                                                                                                    id=37,
                                                                                                    children=[
                                                                                                        Node(
                                                                                                            "Thoracic5",
                                                                                                            id=38,
                                                                                                            children=[
                                                                                                                Node(
                                                                                                                    "Thoracic4",
                                                                                                                    id=39,
                                                                                                                    children=[
                                                                                                                        Node(
                                                                                                                            "Thoracic3",
                                                                                                                            id=40,
                                                                                                                            children=[
                                                                                                                                Node(
                                                                                                                                    "Thoracic2",
                                                                                                                                    id=41,
                                                                                                                                    children=[
                                                                                                                                        Node(
                                                                                                                                            "Thoracic1",
                                                                                                                                            id=42,
                                                                                                                                        ),
                                                                                                                                    ],
                                                                                                                                ),
                                                                                                                            ],
                                                                                                                        ),
                                                                                                                    ],
                                                                                                                ),
                                                                                                            ],
                                                                                                        ),
                                                                                                    ],
                                                                                                ),
                                                                                            ],
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ],
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

BODY_53 = BODY_43

# NOTE: The following import is required for compatibility with existing client code.
# It can be removed after refactoring the client code to eliminate this dependency.
# HAND_21 (hand-only skeleton with 21 joints)
HAND_21 = Node("Wrist", id=0, children=[])
FACE_106 = Node("Nose", id=0, children=[])

WHOLEBODY_150 = COCO_133
