import logging
import platform
import re
import subprocess
from typing import Dict, List, Optional

import cv2


def get_camera_hardware_linux(cam_id):
    # Prepare the external command to extract serial number.
    p = subprocess.Popen(
        f'udevadm info --query=all /dev/video{cam_id} | grep "ID_"',
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


def get_camera_hardware_windows(cam_id):
    # Use WMIC to get camera info
    # WMIC class Win32_PnPEntity can be used to get device details
    cmd = "wmic path Win32_PnPEntity where \"Service='usbvideo'\" get DeviceID,Manufacturer,Name,PNPDeviceID /format:list"
    output = subprocess.check_output(cmd, shell=True, text=True)

    devices = []
    device = {}
    for line in output.splitlines():
        if line.strip() == "":
            if device:
                devices.append(device)
                device = {}
        else:
            if "=" in line:
                key, value = line.split("=", 1)
                device[key.strip()] = value.strip()
    if device:
        devices.append(device)

    info = {}
    if cam_id < len(devices):
        cam = devices[cam_id]
        info["manufacturer"] = cam.get("Manufacturer", "")
        info["model"] = cam.get("Name", "")
        # Attempt to extract serial from PNPDeviceID
        pnp_id = cam.get("PNPDeviceID", "")
        serial_match = re.search(
            r"VID_\w+&PID_\w+&(?:REV_\w+&)?(?:SERIALNUMBER_|SERNUM_)([^&]+)",
            pnp_id,
            re.IGNORECASE,
        )
        if serial_match:
            info["serial"] = serial_match.group(1)
        else:
            info["serial"] = ""
    else:
        logging.error(f"No camera found with id {cam_id} on Windows.")

    return info


def get_camera_hardware_macos(cam_id):
    # Use system_profiler to get camera info
    cmd = "system_profiler SPCameraDataType"
    output = subprocess.check_output(cmd, shell=True, text=True)

    cameras = []
    current_camera = {}
    for line in output.splitlines():
        if line.startswith("Model ID:"):
            if current_camera:
                cameras.append(current_camera)
                current_camera = {}
            current_camera["model_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Vendor ID:"):
            current_camera["vendor_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Unique ID:"):
            current_camera["unique_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("Board ID:"):
            current_camera["board_id"] = line.split(":", 1)[1].strip()

    if current_camera:
        cameras.append(current_camera)

    info = {}
    if cam_id < len(cameras):
        cam = cameras[cam_id]
        info["manufacturer"] = cam.get("vendor_id", "")
        info["model"] = cam.get("model_id", "")
        info["serial"] = cam.get("unique_id", "")
    else:
        logging.error(f"No camera found with id {cam_id} on macOS.")

    return info


def get_camera_hardware(cam_id: int) -> Optional[Dict[str, str]]:
    """
    Retrieves camera hardware information including manufacturer, model, and serial number.

    Parameters:
        cam_id (int): The camera device ID (e.g., 0 for /dev/video0 on Linux).

    Returns:
        dict: A dictionary containing 'manufacturer', 'model', and 'serial' keys.
              Returns None if the information cannot be retrieved.
    """
    system = platform.system()
    default = {
        "manufacturer": "Unknown",
        "model": f"CAM{cam_id}",
        "serial": "",
    }

    try:
        if system == "Linux":
            return get_camera_hardware_linux(cam_id)

        if system == "Windows":
            return get_camera_hardware_windows(cam_id)

        if system == "Darwin":
            return get_camera_hardware_macos(cam_id)

        raise Exception(f"Unsupported platform: {system}")
    except Exception as ex:
        logging.error(f"Error retrieving camera hardware information: {ex}")
        return default


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
