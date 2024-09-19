import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import cv2
import xml.etree.ElementTree as ET
def df_from_trc(trc_path):
    '''
    Retrieve header and data from trc path.
    '''

    # DataRate	CameraRate	NumFrames	NumMarkers	Units	OrigDataRate	OrigDataStartFrame	OrigNumFrames
    df_header = pd.read_csv(trc_path, sep="\t", skiprows=1, header=None, nrows=2, encoding="ISO-8859-1")
    header = dict(zip(df_header.iloc[0].tolist(), df_header.iloc[1].tolist()))
    
    # Label1_X  Label1_Y    Label1_Z    Label2_X    Label2_Y
    df_lab = pd.read_csv(trc_path, sep="\t", skiprows=3, nrows=1)
    labels = df_lab.columns.tolist()[2:-1:3]
    labels_XYZ = np.array([[labels[i]+'_X', labels[i]+'_Y', labels[i]+'_Z'] for i in range(len(labels))], dtype='object').flatten()
    labels_FTXYZ = np.concatenate((['Frame#','Time'], labels_XYZ))
    
    data = pd.read_csv(trc_path, sep="\t", skiprows=5, index_col=False, header=None, names=labels_FTXYZ)
    
    return header, data


connections = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [3,5],
    [3,6],
    [0,7],
    [7,8],
    [8,9],
    [9,10],
    [9,11],
    [9,12],
    [0,13],
    [13,15],
    [15,14],
    [13,16],
    [16,17],
    [17,18],
    [13,19],
    [19,20],
    [20,21]
]

def parse_osim_file(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find the MarkerSet
    markerset = root.find(".//MarkerSet")
    if markerset is None:
        raise ValueError("MarkerSet not found in the file")

    # Extract marker information
    markers = []
    for marker in markerset.findall(".//Marker"):
        name = marker.get("name")
        location_text = marker.find("location").text
        location = list(map(float, location_text.split()))
        markers.append({"name": name, "location": location})

    return markers

if __name__ == '__main__':
    argsparse = argparse.ArgumentParser(description='Visualize trc file.')
    argsparse.add_argument('--trc', type=str, help='Path to trc file.')
    args = argsparse.parse_args()
    trc_path = args.trc
    osim_path = r"E:\Uni\MonocularSystems\HiWi\output\Experiment_2024-09-17_17-31-16\scaled_model.osim"
    header, data = df_from_trc(trc_path)
    bodyparts = np.array([d[:-2] for d in data.columns[2::3]])
    xs = None
    ys = None
    zs = None
    # load the osim file and extract the coordinates of the bodyparts
    ys_osim = None
    zs_osim = None
    markers = parse_osim_file(osim_path)
    xs_osim = [ marker['location'][0] for marker in markers ]
    ys_osim = [ marker['location'][1] for marker in markers ]
    zs_osim = [ marker['location'][2] for marker in markers ]
    # for marker in markers:
    #     print(f"Marker: {marker['name']}, Location: {marker['location']}")
    #     if xs_osim is None:

    pass
    for bp in bodyparts:
        bp_X = bp+'_X'
        bp_Y = bp+'_Y'
        bp_Z = bp+'_Z'
        if xs is None:
            xs = np.array((data[bp_X])).reshape(-1,1)
            ys = np.array((data[bp_Y])).reshape(-1,1)
            zs = np.array((data[bp_Z])).reshape(-1,1)
        else:
            xs = np.concatenate((xs, np.array((data[bp_X])).reshape(-1,1)), axis=1)
            ys = np.concatenate((ys, np.array((data[bp_Y])).reshape(-1,1)), axis=1)
            zs = np.concatenate((zs, np.array((data[bp_Z])).reshape(-1,1)), axis=1)
    print(xs.shape, ys.shape, zs.shape)
    os.makedirs('./images/', exist_ok=True)
    for i in range(xs.shape[0]):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(zs[i],xs[i], ys[i])
        if np.isnan(xs[i]).any():
            index_of_nan = np.where(np.isnan(xs[i]))
            print(f"NaN in xs at frame {i}",index_of_nan, xs[i])
        if np.isnan(ys[i]).any():
            index_of_nan = np.where(np.isnan(ys[i]))
            print(f"NaN in ys at frame {i}",index_of_nan, ys[i])
        if np.isnan(zs[i]).any():
            index_of_nan = np.where(np.isnan(zs[i]))
            print(f"NaN in zs at frame {i}",index_of_nan, zs[i])
        break
        #ax.scatter(zs_osim, xs_osim, ys_osim)
        # for j in range(len(zs_osim)):
        #     ax.text(zs_osim[j], xs_osim[j], ys_osim[j], markers[j]['name'])
        for j in range(len(zs[i])):
            ax.text(zs[i][j], xs[i][j], ys[i][j], bodyparts[j])
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        # each axis should have the same length
        ax.view_init(elev=15, azim=79)
        # save the image and make a video out of it
        plt.show()
    # make video on windows with cv2
    # img_array = []
    # for filename in sorted(os.listdir('./images/'), key=lambda x: int(x.split('.')[0])):
    #     if filename.endswith('.png'):
    #         print(filename)
    #         img = cv2.imread(os.path.join("./images/",filename))
    #         height, width, layers = img.shape
    #         size = (width,height)
    #         img_array.append(img)
    # out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 60, size)
    # for i in range(len(img_array)):
    #     out.write(img_array[i])
    # out.release()
