from typing import List, Dict

import cv2


def get_camera_info(camera_id):
    if isinstance(camera_id, int) or camera_id.isdigit():
        camera = cv2.VideoCapture(int(camera_id))
        if not camera.isOpened():
            return None

        info = {
            "id": camera_id,
            "width": int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(camera.get(cv2.CAP_PROP_FPS)),
        }
        camera.release()
        return info

    return None


def find_cameras(max_cameras=5) -> List[Dict]:
    """ Find available cameras.

    Args:
        max_cameras (int): Maximum number of cameras to search for.
    """
    info = []
    for i in range(max_cameras):
        camera = get_camera_info(i)
        if camera:
            info.append(camera)
    return info
