import logging

logger = logging.getLogger(__name__)

import cv2
import matplotlib.pyplot as plt
import numpy as np

try:
    from sam2.build_sam import build_sam2_camera_predictor
except ImportError:
    logger.warning("sam2 not found, tracking will be disabled")
    logger.warning("see https://github.com/Gy920/segment-anything-2-real-time")
    build_sam2_camera_predictor = None


class SAM2LiveTracker:
    def __init__(self):
        self._predictor = None
        self._is_init = False
        if build_sam2_camera_predictor is not None:
            checkpoint = "assets/sam2_hiera_tiny.pt"
            model_cfg = "sam2_hiera_t.yaml"
            self._predictor = build_sam2_camera_predictor(model_cfg, checkpoint)

    @property
    def is_available(self):
        return self._predictor is not None
    
    @property
    def is_init(self):
        return self._is_init
    
    def init(self, frame, prompt, frame_idx=0, obj_id=0):
        if self._predictor is None:
            return -1, None

        self._predictor.load_first_frame(frame)
        _, out_obj_ids, out_mask_logits = self._predictor.add_new_prompt(
            frame_idx=frame_idx,
            obj_id=obj_id,
            points=np.array([prompt], dtype=np.float32),
            labels=np.array([1], np.int32),
        )
        self._is_init = True
        return out_obj_ids[0], out_mask_logits[0]

    def reset(self):
        if self._is_init:
            self._predictor.reset_state()

        self._is_init = False

    def track(self, frame):
        if not self._is_init or self._predictor is None:
            return -1, None

        return self._predictor.track(frame)

    def mask2bbox(self, mask):
        if mask is None:
            return None

        # find contours
        mask = mask.astype(np.uint8)[0]
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # merge all contours into one bounding box
        if len(contours) < 1:
            return None

        bboxes = [cv2.boundingRect(c) for c in contours]
        x = min([bbox[0] for bbox in bboxes])
        y = min([bbox[1] for bbox in bboxes])
        w = max([bbox[0] + bbox[2] for bbox in bboxes]) - x
        h = max([bbox[1] + bbox[3] for bbox in bboxes]) - y
        return (x, y, w, h)

    def visualize(self, frame, track_result, random_color=False):
        obj_id, mask_logits = track_result
        if mask_logits is None:
            return frame, None

        # set mask color
        if random_color:
            color = np.random.rand(3).tolist() + [0.6]
        else:
            cmap = plt.get_cmap("tab10")
            cmap_idx = 0 if obj_id is None else obj_id
            color = list(cmap(cmap_idx)[:3]) + [0.6]

        # create mask
        mask = (mask_logits > 0.0).cpu().numpy()
        h, w = mask.shape[-2:]
        mask = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)  # in [0, 1]

        # overlay mask on frame
        vis = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)  # in [0, 255]
        vis = vis.astype(np.float32) / 255.0
        vis *= (1 - mask)
        vis += mask
        vis = (vis * 255).astype(np.uint8)
        vis = cv2.cvtColor(vis, cv2.COLOR_BGRA2BGR)

        # draw bounding box
        bbox = self.mask2bbox(mask_logits)

        return vis, bbox