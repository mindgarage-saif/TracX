import subprocess
from typing import Dict, List

import cv2


def get_camera_hardware(cam_id):
    # Prepare the external command to extract serial number.
    p = subprocess.Popen(
        'udevadm info --query=all /dev/video{} | grep "ID_"'.format(cam_id),
        stdout=subprocess.PIPE,
        shell=True,
    )

    # Run the command
    (output, err) = p.communicate()

    # Wait for it to finish
    p.status = p.wait()

    # Decode the output
    response = output.decode("utf-8")

    # Parse response to get hardware info
    response = response.split("\n")
    info = {}
    for line in response:
        line = line.strip()
        if line:
            key = line.split("=")[0].split(":")[1].strip()
            value = line.split("=")[1]
            info[key] = value
    return {
        "manufacturer": info["ID_VENDOR"].replace("_", " "),
        "model": info["ID_MODEL"].replace("_", " ") + f" {info['ID_MODEL_ID']}",
        "serial": info["ID_SERIAL"].replace("_", " "),
    }


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
            **get_camera_hardware(camera_id),
        }
        camera.release()
        return info

    return None


def find_cameras(max_cameras=5) -> List[Dict]:
    """Find available cameras.

    Args:
        max_cameras (int): Maximum number of cameras to search for.
    """
    info = []
    for i in range(max_cameras):
        camera = get_camera_info(i)
        if camera:
            info.append(camera)
    return info
