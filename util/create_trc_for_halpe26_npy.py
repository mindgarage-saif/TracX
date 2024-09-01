import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # This import registers the 3D projection
import os
import pandas as pd
import argparse
"""
Some code snippets where taken from the Pose2Sim repository https://github.com/perfanalytics/pose2sim
"""
def createDic(list):
    new_dict = {}
    for i in range(len(list)):
        new_dict[list[i]] = i
    return new_dict

def  readTrc_header(path_to_trc,header_info=None,from_reference=False):
    print('reading trc file')
    if from_reference:
        with open(path_to_trc, 'r') as trc_file:
            lines = trc_file.readlines()
            header = lines[:5]
            print(len(header))
            return header
    else:
        file_name = header_info.file_name
        data_rate = header_info.data_rate
        frame_rate = header_info.frame_rate
        og_data_rate = header_info.og_data_rate
        num_of_frames = header_info.num_of_frames
        num_of_markers = header_info.num_of_markers # we only triangulate 22 of the 26 halpe joints
        strat_frame = header_info.num_of_markers
        end_frame = header_info.end_frame
        header_line_0 = 'PathFileType\t4\t(X/Y/Z)\t' + file_name + '\n'
        header_line_1 = 'DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n'
        header_line_2 = f'{data_rate}\t{frame_rate}\t{num_of_frames}\t{num_of_markers}\tm\t{og_data_rate}\t{strat_frame}\t{end_frame}\n'
        header_line_3 = 'Frame#\tTime\tHip\t\t\tRHip\t\t\tRKnee\t\t\tRAnkle\t\t\tRBigToe\t\t\tRSmallToe\t\t\tRHeel\t\t\tLHip\t\t\tLKnee\t\t\tLAnkle\t\t\tLBigToe\t\t\tLSmallToe\t\t\tLHeel\t\t\tNeck\t\t\tHead\t\t\tNose\t\t\tRShoulder\t\t\tRElbow\t\t\tRWrist\t\t\tLShoulder\t\t\tLElbow\t\t\tLWrist\t\t\n'
        header_line_4 = '\t\t'+'\t'.join([f'X{i+1}\tY{i+1}\tZ{i+1}' for i in range(22)]) + '\n'
        print([header_line_0,header_line_1,header_line_2,header_line_3,header_line_4])
        return [header_line_0,header_line_1,header_line_2,header_line_3,header_line_4]

def readTrc(path_to_3d_joints):
    with open(path_to_3d_joints, 'r') as trc_file:
        lines = trc_file.readlines()
        joints = []
        joint_names = lines[3].split('\t')[2:] # remove empty string
        elem = joint_names[-1]
        elem2 = joint_names[1]
        for line in lines[5:]:
            joint = line.replace('\n','').split('\t')[2:]
            xs = np.array(joint[::3],dtype=np.float64)
            ys = np.array(joint[1::3],dtype=np.float64)
            zs = np.array(joint[2::3],dtype=np.float64)
            joints.append([[z,x,y] for x,y,z in zip(xs,ys,zs)])
        joint_names.remove(elem2)
        new_joint_names = list(filter((elem2).__ne__, joint_names))
        new_joint_names = list(filter((elem).__ne__, new_joint_names))
        joint_to_idx = createDic(new_joint_names)
    return np.array(joints,dtype=np.float64),joint_to_idx

# def vis_npy(npy_path,path_to_3d_joints, save_path=None):
#     data = np.load(npy_path)
#     joints_3d,_ = readTrc(path_to_3d_joints)
#     for i, frame in enumerate(data):
#         if i % 20 != 0:
#             continue
#         joints_before = joints_3d[i]
#         joints_after = frame[0]
#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot
#         x = joints_after[:, 0]
#         y = joints_after[:, 1]
#         z = joints_after[:, 2]
#         a = joints_before[:, 0]
#         b = joints_before[:, 1]
#         c = joints_before[:, 2]
#         ax.scatter(x, y, z, c='r')  # Plot the 3D points
#         ax.scatter(a, b, c, c='b')  # Plot the 3D points
#         ax.set_xlabel('X Label')
#         ax.set_ylabel('Y Label')
#         ax.set_zlabel('Z Label')
#         max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max()
#         Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(x.max()+x.min())
#         Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(y.max()+y.min())
#         Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(z.max()+z.min())
#         for xb, yb, zb in zip(Xb, Yb, Zb):
#             ax.plot([zb], [xb], [yb], 'w')
#         if save_path is not None:
#             plt.savefig(save_path)
#         plt.show()
#         plt.close(fig)

def store_npy_halpe26_to_trc(npy_path, trc_path,out_put,header_info,from_reference):
    data = np.load(npy_path)
    data = data.reshape(data.shape[0],data.shape[2],data.shape[3])
    data = data[:,:,[1,2,0]]
    frame_rate = 60
    frame_num = data.shape[0]
    header = readTrc_header(trc_path,header_info,from_reference)

    q_prime = pd.DataFrame(data.reshape(data.shape[0], -1))
    q_prime.index = np.array(range(0, frame_num)) + 1
    q_prime.insert(0, 't', q_prime.index / frame_rate)
    new_trc_path = out_put
    print(f"Writing to {new_trc_path}")
    with open(new_trc_path, 'w') as trc_o:
        [trc_o.write(line) for line in header]
        q_prime.to_csv(trc_o, sep='\t', index=True, header=None, lineterminator='\n')

if __name__ == '__main__':
    argsp = argparse.ArgumentParser()
    argsp.add_argument("--npy_path",default=r"C:\Users\Jeremias\Documents\Uni\HIWI_DFKI\Pose2SimPipeline\Pipeline\enhanced_3d_joints_with_weighted_feet_and_hip.npy", type=str, help="Path to the npy file")
    argsp.add_argument("--trc_path",default=r"C:\Users\Jeremias\anaconda3\envs\Pose2Sim\Lib\site-packages\Pose2Sim\RMTPoseL\RMTPoseL\ROM2\3c\23087_29092_29913\ROM2_RTMPose_0-3038_filt_butterworth.trc", type=str, help="Path to the trc file")
    argsp.add_argument("--header_info",default=False, type=bool, help="Header information")
    argsp.add_argument("--from_reference",default=False, type=bool, help="Read from reference")
    argsp.add_argument("--file_name",default='Generic_Name.trc', type=str, help="File name")    
    argsp.add_argument("--data_rate",default=60, type=int, help="Data rate")
    argsp.add_argument("--frame_rate",default=60, type=int, help="Frame rate")
    argsp.add_argument("--og_data_rate",default=60, type=int, help="Original data rate")
    argsp.add_argument("--num_of_frames",default=1800, type=int, help="Number of frames")
    argsp.add_argument("--strat_frame",default=0, type=int, help="Start frame")
    argsp.add_argument("--end_frame",default=1799, type=int, help="End frame")
    argsp.add_argument("--out_put",default='Generic_Name.trc', type=str, help="Output file name")
    args = argsp.parse_args()
    if args.header_info:
        file_name = args.file_name
        data_rate = args.data_rate
        frame_rate = args.frame_rate
        og_data_rate = args.og_data_rate
        num_of_frames = args.num_of_frames
        num_of_markers = 22 # we only triangulate 22 of the 26 halpe joints
        strat_frame = args.strat_frame
        end_frame = args.end_frame
        header_info = {'file_name':file_name,
                       'data_rate':data_rate,
                       'frame_rate':frame_rate,
                       'og_data_rate':og_data_rate,
                       'num_of_frames':num_of_frames,
                       'num_of_markers':num_of_markers,
                       'strat_frame':strat_frame,
                       'end_frame':end_frame}
    else:
        file_name = 'Generic_Name.trc'
        data_rate = 60
        frame_rate = 60
        og_data_rate = 60
        num_of_frames = 1800
        num_of_markers = 22
        strat_frame = 0
        end_frame = 1799
        header_info = {'file_name':file_name,
                       'data_rate':data_rate,
                       'frame_rate':frame_rate,
                       'og_data_rate':og_data_rate,
                       'num_of_frames':num_of_frames,
                       'num_of_markers':num_of_markers,
                       'strat_frame':strat_frame,
                       'end_frame':end_frame}
    store_npy_halpe26_to_trc(args.npy_path,args.trc_path,args.out_put,header_info,args.from_reference)

    #     file_name = header_info.file_name
    #     data_rate = header_info.data_rate
    #     frame_rate = header_info.frame_rate
    #     og_data_rate = header_info.og_data_rate
    #     num_of_frames = header_info.num_of_frames
    #     num_of_markers = header_info.num_of_markers # we only triangulate 22 of the 26 halpe joints
    #     strat_frame = header_info.num_of_markers
    #     end_frame = header_info.end_frame