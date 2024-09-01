import cv2
import numpy as np
import argparse
import os
import xml.etree.ElementTree as ET
# Open the video file
videoNameDic = { 'clockwise': ['Gait Markerless 3_Miqus_5_29092', 'Gait Markerless 3_Miqus_8_29913'],
                    'counterclockwise': ['Gait Markerless 3_Miqus_2_29089','Gait Markerless 3_Miqus_4_24994','Gait Markerless 3_Miqus_1_23087','Gait Markerless 3_Miqus_9_29090'],
                    'upside-down': ['Gait Markerless 3_Miqus_3_28984','Gait Markerless 3_Miqus_6_28983','Gait Markerless 3_Miqus_7_23138']
                }
def rotate(input_dir,output_dir):
    for rot in videoNameDic.keys():
        for videoName in videoNameDic[rot]:
            cap = cv2.VideoCapture(os.path.join(input_dir, videoName +".avi"))
            print("lol")
            # Get original video's width, height, and fps
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Create a VideoWriter object
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if rot == 'upside-down':
                out = cv2.VideoWriter(os.path.join(output_dir, videoName +"_rot.avi"), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
            else:
                out = cv2.VideoWriter(os.path.join(output_dir, videoName +"_rot.avi"), cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_height, frame_width))

            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret == True:
                    # Rotate the frame
                    if rot == 'upside-down':
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif rot == 'counterclockwise':
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif rot == 'clockwise':
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    
                    # Write the rotated frame to the new video file
                    out.write(frame)
                else:
                    break

            # Release the VideoCapture and VideoWriter objects
            cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rotate videos')
    parser.add_argument('--input_dir', type=str, help='Input directory containing videos')
    parser.add_argument('--output_dir', type=str, help='Output directory to save rotated videos')
    args = parser.parse_args()
    rotate(args.input_dir, args.output_dir)