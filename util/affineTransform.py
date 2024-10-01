import cv2 as cv
import numpy as np

# Open the video file
cap = cv.VideoCapture(
    r"E:\Uni\Data\LIHS\LIHS\ROM_1_videos_rot\Generic Markerless 1_Miqus_1_23087_rot.avi"
)

# Define the codec and create a VideoWriter object
fourcc = cv.VideoWriter_fourcc(*"mp4v")  # or use 'XVID'
out = cv.VideoWriter("output.mp4", fourcc, 60.0, (1080, 1920))

# Define the transformation
pts1 = np.float32([[0, 1900], [1080, 1900], [0, 0], [1080, 0]])
pts2 = np.float32([[0, 1900], [1080, 1900], [250, 550], [830, 550]])
M = cv.getPerspectiveTransform(pts1, pts2)

while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        # Apply the transformation
        dst = cv.warpPerspective(frame, M, (1080, 1920))

        # Write the transformed frame to the output video
        out.write(dst)
    else:
        break

# Release everything when done
cap.release()
out.release()
