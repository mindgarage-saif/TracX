import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import os
import statistics
import cv2
import numpy as np
import matplotlib.cm as cm

def vis_theia_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    cmap = cm.get_cmap('hsv')
    frames = data['frames']

    connections = {
        0: [1, 4, 7],
        1: [2],
        2: [3],
        4: [5],
        5: [6],
        7: [14, 8, 11],
        8: [9],
        9: [10],
        11: [12],
        12: [13]
    }
    lableMarkers = {
        0: 'Pelvis',
        1: 'RHip',
        2: 'RKnee',
        3: 'RAnkle',
        4: 'LHip',
        5: 'LKnee',
        6: 'LAnkle',
        7: 'Thorax',
        8: 'RShoulder',
        9: 'RElbow',
        10: 'RWrist',
        11: 'LShoulder',
        12: 'LElbow',
        13: 'LWrist',
        14: 'Head',
    }
    rotations = {
        0: 'Pelvis_wrt_Lab',
        3: 'RFoot_wrt_Lab',
        6: 'LFoot_wrt_Lab',
        '1-2': 'RThigh_wrt_Lab',
        '2-3': 'RLeg_wrt_Lab',
        '4-5': 'LThigh_wrt_Lab',
        '5-6': 'LLeg_wrt_Lab',
        7: 'Thorax_wrt_Lab',
        '8-9': 'RArm_wrt_Lab',
        '9-10': 'RForearm_wrt_Lab',
        10: 'RHand_wrt_Lab',
        '11-12': 'LArm_wrt_Lab',
        '12-13': 'LForearm_wrt_Lab',
        13: 'LHand_wrt_Lab',
        14: 'Head_wrt_Lab',

    }
    if not os.path.exists('img3d'):
        os.makedirs('img3d')
    y = 0
    for frame_index, frame in enumerate(frames):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=0, azim=90)  # Look onto the y-axis
        #ax.set_box_aspect([4800/1700, 600/1700, 1])  # Set the aspect ratio of the axes
        # segmentPos = [[coord/1000 for coord in point] for point in frame['segmentPos']]
        segmentPos = frame['segmentPos']

        avg_x = statistics.mean(point[0] for point in segmentPos)
        avg_y = statistics.mean(point[1] for point in segmentPos)
        avg_z = statistics.mean(point[2] for point in segmentPos)
        o = 0
        handles2 = []
        labels2 = []
        for i, point in enumerate(segmentPos):
            points = ax.scatter(point[0], point[1], point[2], label=f"{i} {lableMarkers[i]}")
            ax.text(point[0], point[1], point[2], '%s' % (str(i)), size=13, zorder=i, color='k')
            if i in connections:
                for connection in connections[i]:
                    color = cmap(o/len(segmentPos))
                    o += 1
                    line, = ax.plot([point[0], segmentPos[connection][0]], 
                            [point[1], segmentPos[connection][1]], 
                            [point[2], segmentPos[connection][2]], color=color)

        ax.set_xlim3d(avg_x -500, avg_x +500)
        ax.set_ylim3d(avg_y - 500, avg_y + 500)
        ax.set_zlim3d(0, 1700)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        legend1 = ax.legend(bbox_to_anchor=(1.2, 1))
        ax.add_artist(legend1)
        plt.show()
        # plt.savefig(f'img3d/frame_{frame_index}.png')
        # plt.close(fig)

def create_video(image_folder, video_name, fps):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()
if __name__ == '__main__':  
    vis_theia_json(r"E:\Uni\Data\LIHS\LIHS\ROM_2\ROM_2\Generic Markerless 2-3d-data.json")
# create_video('img3d', '3d_animation.avi', 60)