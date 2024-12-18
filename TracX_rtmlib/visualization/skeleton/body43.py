body43 = dict(
    name="body43",
    keypoint_info={
        0: dict(name="nose", id=0, color=[51, 153, 255], type="upper", swap=""),
        1: dict(
            name="left_eye", id=1, color=[51, 153, 255], type="upper", swap="right_eye"
        ),
        2: dict(
            name="right_eye", id=2, color=[51, 153, 255], type="upper", swap="left_eye"
        ),
        3: dict(
            name="left_ear", id=3, color=[51, 153, 255], type="upper", swap="right_ear"
        ),
        4: dict(
            name="right_ear", id=4, color=[51, 153, 255], type="upper", swap="left_ear"
        ),
        5: dict(
            name="left_shoulder",
            id=5,
            color=[0, 255, 0],
            type="upper",
            swap="right_shoulder",
        ),
        6: dict(
            name="right_shoulder",
            id=6,
            color=[255, 128, 0],
            type="upper",
            swap="left_shoulder",
        ),
        7: dict(
            name="left_elbow", id=7, color=[0, 255, 0], type="upper", swap="right_elbow"
        ),
        8: dict(
            name="right_elbow",
            id=8,
            color=[255, 128, 0],
            type="upper",
            swap="left_elbow",
        ),
        9: dict(
            name="left_wrist", id=9, color=[0, 255, 0], type="upper", swap="right_wrist"
        ),
        10: dict(
            name="right_wrist",
            id=10,
            color=[255, 128, 0],
            type="upper",
            swap="left_wrist",
        ),
        11: dict(
            name="left_hip", id=11, color=[0, 255, 0], type="lower", swap="right_hip"
        ),
        12: dict(
            name="right_hip", id=12, color=[255, 128, 0], type="lower", swap="left_hip"
        ),
        13: dict(
            name="left_knee", id=13, color=[0, 255, 0], type="lower", swap="right_knee"
        ),
        14: dict(
            name="right_knee",
            id=14,
            color=[255, 128, 0],
            type="lower",
            swap="left_knee",
        ),
        15: dict(
            name="left_ankle",
            id=15,
            color=[0, 255, 0],
            type="lower",
            swap="right_ankle",
        ),
        16: dict(
            name="right_ankle",
            id=16,
            color=[255, 128, 0],
            type="lower",
            swap="left_ankle",
        ),
        17: dict(name="head", id=17, color=[255, 128, 0], type="upper", swap=""),
        18: dict(name="neck", id=18, color=[255, 128, 0], type="upper", swap=""),
        19: dict(name="hip", id=19, color=[255, 128, 0], type="lower", swap=""),
        20: dict(
            name="left_big_toe",
            id=20,
            color=[255, 128, 0],
            type="lower",
            swap="right_big_toe",
        ),
        21: dict(
            name="right_big_toe",
            id=21,
            color=[255, 128, 0],
            type="lower",
            swap="left_big_toe",
        ),
        22: dict(
            name="left_small_toe",
            id=22,
            color=[255, 128, 0],
            type="lower",
            swap="right_small_toe",
        ),
        23: dict(
            name="right_small_toe",
            id=23,
            color=[255, 128, 0],
            type="lower",
            swap="left_small_toe",
        ),
        24: dict(
            name="left_heel",
            id=24,
            color=[255, 128, 0],
            type="lower",
            swap="right_heel",
        ),
        25: dict(
            name="right_heel",
            id=25,
            color=[255, 128, 0],
            type="lower",
            swap="left_heel",
        ),
        26: dict(name="thoracic_1", id=26, color=[255, 128, 0], type="upper", swap=""),
        27: dict(name="thoracic_2", id=27, color=[255, 128, 0], type="upper", swap=""),
        28: dict(name="thoracic_3", id=28, color=[255, 128, 0], type="upper", swap=""),
        29: dict(name="thoracic_4", id=29, color=[255, 128, 0], type="upper", swap=""),
        30: dict(name="thoracic_5", id=30, color=[255, 128, 0], type="upper", swap=""),
        31: dict(name="thoracic_6", id=31, color=[255, 128, 0], type="upper", swap=""),
        32: dict(name="thoracic_7", id=32, color=[255, 128, 0], type="upper", swap=""),
        33: dict(name="thoracic_8", id=33, color=[255, 128, 0], type="upper", swap=""),
        34: dict(name="thoracic_9", id=34, color=[255, 128, 0], type="upper", swap=""),
        35: dict(name="thoracic_10", id=35, color=[255, 128, 0], type="upper", swap=""),
        36: dict(name="thoracic_11", id=36, color=[255, 128, 0], type="upper", swap=""),
        37: dict(name="thoracic_12", id=37, color=[255, 128, 0], type="upper", swap=""),
        38: dict(name="lumbar_1", id=38, color=[255, 128, 0], type="lower", swap=""),
        39: dict(name="lumbar_2", id=39, color=[255, 128, 0], type="lower", swap=""),
        40: dict(name="lumbar_3", id=40, color=[255, 128, 0], type="lower", swap=""),
        41: dict(name="lumbar_4", id=41, color=[255, 128, 0], type="lower", swap=""),
        42: dict(name="lumbar_5", id=42, color=[255, 128, 0], type="lower", swap=""),
    },
    skeleton_info={
        0: dict(link=("left_ankle", "left_knee"), id=0, color=[0, 255, 0]),
        1: dict(link=("left_knee", "left_hip"), id=1, color=[0, 255, 0]),
        2: dict(link=("left_hip", "hip"), id=2, color=[0, 255, 0]),
        3: dict(link=("right_ankle", "right_knee"), id=3, color=[255, 128, 0]),
        4: dict(link=("right_knee", "right_hip"), id=4, color=[255, 128, 0]),
        5: dict(link=("right_hip", "hip"), id=5, color=[255, 128, 0]),
        6: dict(link=("head", "neck"), id=6, color=[51, 153, 255]),
        7: dict(link=("neck", "left_shoulder"), id=7, color=[0, 255, 0]),
        8: dict(link=("left_shoulder", "left_elbow"), id=8, color=[0, 255, 0]),
        9: dict(link=("left_elbow", "left_wrist"), id=9, color=[0, 255, 0]),
        10: dict(link=("neck", "right_shoulder"), id=10, color=[255, 128, 0]),
        11: dict(link=("right_shoulder", "right_elbow"), id=11, color=[255, 128, 0]),
        12: dict(link=("right_elbow", "right_wrist"), id=12, color=[255, 128, 0]),
        13: dict(link=("left_eye", "right_eye"), id=13, color=[51, 153, 255]),
        14: dict(link=("nose", "left_eye"), id=14, color=[51, 153, 255]),
        15: dict(link=("nose", "right_eye"), id=15, color=[51, 153, 255]),
        16: dict(link=("left_eye", "left_ear"), id=16, color=[51, 153, 255]),
        17: dict(link=("right_eye", "right_ear"), id=17, color=[51, 153, 255]),
        18: dict(link=("left_ear", "left_shoulder"), id=18, color=[51, 153, 255]),
        19: dict(link=("right_ear", "right_shoulder"), id=19, color=[51, 153, 255]),
        20: dict(link=("left_ankle", "left_big_toe"), id=20, color=[0, 255, 0]),
        21: dict(link=("left_ankle", "left_small_toe"), id=21, color=[0, 255, 0]),
        22: dict(link=("left_ankle", "left_heel"), id=22, color=[0, 255, 0]),
        23: dict(link=("right_ankle", "right_big_toe"), id=23, color=[255, 128, 0]),
        24: dict(link=("right_ankle", "right_small_toe"), id=24, color=[255, 128, 0]),
        25: dict(link=("right_ankle", "right_heel"), id=25, color=[255, 128, 0]),
        26: dict(link=("neck", "thoracic_1"), id=26, color=[255, 128, 0]),
        27: dict(link=("thoracic_1", "thoracic_2"), id=27, color=[255, 128, 0]),
        28: dict(link=("thoracic_2", "thoracic_3"), id=28, color=[255, 128, 0]),
        29: dict(link=("thoracic_3", "thoracic_4"), id=29, color=[255, 128, 0]),
        30: dict(link=("thoracic_4", "thoracic_5"), id=30, color=[255, 128, 0]),
        31: dict(link=("thoracic_5", "thoracic_6"), id=31, color=[255, 128, 0]),
        32: dict(link=("thoracic_6", "thoracic_7"), id=32, color=[255, 128, 0]),
        33: dict(link=("thoracic_7", "thoracic_8"), id=33, color=[255, 128, 0]),
        34: dict(link=("thoracic_8", "thoracic_9"), id=34, color=[255, 128, 0]),
        35: dict(link=("thoracic_9", "thoracic_10"), id=35, color=[255, 128, 0]),
        36: dict(link=("thoracic_10", "thoracic_11"), id=36, color=[255, 128, 0]),
        37: dict(link=("thoracic_11", "thoracic_12"), id=37, color=[255, 128, 0]),
        38: dict(link=("thoracic_12", "lumbar_1"), id=38, color=[255, 128, 0]),
        39: dict(link=("lumbar_1", "lumbar_2"), id=39, color=[255, 128, 0]),
        40: dict(link=("lumbar_2", "lumbar_3"), id=40, color=[255, 128, 0]),
        41: dict(link=("lumbar_3", "lumbar_4"), id=41, color=[255, 128, 0]),
        42: dict(link=("lumbar_4", "lumbar_5"), id=42, color=[255, 128, 0]),
        43: dict(link=("lumbar_5", "hip"), id=43, color=[255, 128, 0]),
    },
)
