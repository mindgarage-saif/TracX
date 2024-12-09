from rtmlib.visualization.draw import draw_mmpose, draw_openpose

from .skeleton import *  # noqa


def draw_skeleton(
    img, keypoints, scores, openpose_skeleton=False, kpt_thr=0.5, radius=2, line_width=2
):
    num_keypoints = keypoints.shape[1]

    if openpose_skeleton:
        if num_keypoints == 18:
            skeleton = "openpose18"
        elif num_keypoints == 134:
            skeleton = "openpose134"
        elif num_keypoints == 26:
            skeleton = "halpe26"
        else:
            raise NotImplementedError
    else:
        if num_keypoints == 17:
            skeleton = "coco17"
        elif num_keypoints == 133:
            skeleton = "coco133"
        elif num_keypoints == 21:
            skeleton = "hand21"
        elif num_keypoints == 26:
            skeleton = "halpe26"
        elif num_keypoints == 43:
            skeleton = "body43"
        elif num_keypoints == 53:
            skeleton = "body53"
        elif num_keypoints == 106:
            skeleton = "face106"
        elif num_keypoints == 150:
            skeleton = "wholebody150"
        else:
            raise NotImplementedError

    skeleton_dict = eval(f"{skeleton}")
    keypoint_info = skeleton_dict["keypoint_info"]
    skeleton_info = skeleton_dict["skeleton_info"]

    if len(keypoints.shape) == 2:
        keypoints = keypoints[None, :, :]
        scores = scores[None, :, :]

    num_instance = keypoints.shape[0]
    if skeleton in [
        "coco17",
        "coco133",
        "hand21",
        "halpe26",
        "body43",
        "body53",
        "face106",
        "wholebody150",
    ]:
        for i in range(num_instance):
            img = draw_mmpose(
                img,
                keypoints[i],
                scores[i],
                keypoint_info,
                skeleton_info,
                kpt_thr,
                radius,
                line_width,
            )
    elif skeleton in ["openpose18", "openpose134"]:
        for i in range(num_instance):
            img = draw_openpose(
                img,
                keypoints[i],
                scores[i],
                keypoint_info,
                skeleton_info,
                kpt_thr,
                radius * 2,
                alpha=0.6,
                line_width=line_width * 2,
            )
    else:
        raise NotImplementedError
    return img
