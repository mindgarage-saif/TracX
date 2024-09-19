import os
from Pose2Sim import Pose2Sim
import argparse
from util.rotate2dBack import *
import argparse
# import date and time
import datetime
from util.rotator import rotate
import shutil
from util.OpenSim_create import create_opensim
import glob
from Pose2Sim.Utilities import bodykin_from_mot_osim
def execute_pose2sim_triangluation(path,should_sync = False, with_marker_augmentation = False):
    os.chdir(path)
    Pose2Sim.calibration('./')
    Pose2Sim.personAssociation('./')
    if should_sync:
        Pose2Sim.synchronization('./')
    Pose2Sim.triangulation('./')
    Pose2Sim.filtering('./')
    if with_marker_augmentation:
        Pose2Sim.markerAugmentation('./')

def execute_2d_detection(path):
    Pose2Sim.poseEstimation(path)

def prepare_videos(path_to_video_dir,camera_parameters_path,should_rotate,exp_name):
    if exp_name and not os.path.exists(os.path.join("experiments",exp_name,'videos')):
        os.makedirs(os.path.join("experiments",exp_name,'videos'))
    else:
        # Get the current date and time
        exp_name = f'Experiment_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        os.makedirs(os.path.join("experiments",exp_name,'videos'))
    if should_rotate:
        rotate(path_to_video_dir,os.path.join("experiments",exp_name,'videos'),camera_parameters_path)
    else:
        for video in os.listdir(path_to_video_dir):
            # moves the video to the videos folder. Can be changed to copy if needed or swapped out entirely. Because Pose2Sim doesnt nativly allow to give paths but allways assumes the current dir or the the provided dir is the experiment directory with the config file in it.
            if not video.endswith('.mp4') or not video.endswith('.avi'):
                continue
            shutil.move(os.path.join(path_to_video_dir,video),os.path.join(exp_name,'videos',video))
    return os.path.join('experiments',exp_name),exp_name

def main(video_dir,camera_parameters,rotate,config,exp_name,sync,marker_augmentation,opensim,blender):
    assert config.endswith('.toml'), "The config file should be a toml file"
    #Moves the videos into the experiment folder, such that they are in the same location as the config file.
    # And creates the experiment folder
    path_to_exp,exp_name = prepare_videos(video_dir,camera_parameters,rotate,exp_name)
    shutil.copyfile(config,os.path.join(path_to_exp,'Config.toml'))

    if not (os.path.exists(os.path.join(path_to_exp,'pose')) and os.path.exists(os.path.join(path_to_exp,'pose_rotated'))):
        execute_2d_detection(path_to_exp)
        if rotate:
            rotate2dBack(os.path.join(path_to_exp,'pose'),camera_parameters)
            shutil.move(os.path.join(path_to_exp,'pose_rotated'), os.path.join(path_to_exp,'pose'))

    os.makedirs(os.path.join(path_to_exp,'calibration'),exist_ok=True)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!!! Assumes file to be in QCA camera format. It doesnt matter if it is in XML file format or txt file format. But internaly it has to be in QCA format.!!!!!!!!
    shutil.copyfile(camera_parameters,os.path.join(path_to_exp,'calibration','camera_parameters.qca.txt'))
    execute_pose2sim_triangluation(path_to_exp,sync,marker_augmentation)
    os.chdir(os.path.join(os.getcwd(),"../../"))
    path_to_trc = glob.glob(os.path.join(path_to_exp,'pose-3d','*_filt_butterworth.trc'))[0]
    if opensim:
        output,mot,scaled_model = create_opensim(path_to_trc,exp_name)
        if blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(mot,scaled_model,os.path.join(output,'bodykin.csv'))
    

if __name__ == '__main__':
    argspaser = argparse.ArgumentParser()
    argspaser.add_argument("--config",required=True,default=r"E:\Uni\MonocularSystems\HiWi\Data\experiments\new\LIHS\ROM2", type=str, help="Path to the config file")
    argspaser.add_argument("--sync",default=False, type=bool, help="Sync the data")
    argspaser.add_argument("--marker_augmentation",default=False, type=bool, help="Marker augmentation")
    argspaser.add_argument("--camera_parameters",required=True,default=r"E:\Uni\MonocularSystems\HiWi\Gait Markerless 2.settings_new.xml", type=str, help="Path to the camera XML file")
    argspaser.add_argument('--video_dir',required=True, type=str, help="Path to the video directory, which only contains the videos")
    argspaser.add_argument('--rotate', default=False, type=bool, help="Should rotate the the videos")
    argspaser.add_argument('--exp_name', default=None, type=str, help="Should sync the the videos")
    argspaser.add_argument('--opensim', default=True, type=bool, help="Createse opensim files")
    argspaser.add_argument('--blender', default=True, type=bool, help="Also returns the CSV files for blender")
    args = argspaser.parse_args()
    main(args.video_dir,args.camera_parameters,args.rotate,args.config,args.exp_name,args.sync,args.marker_augmentation,args.opensim,args.blender)
    # assert args.config.endswith('.toml'), "The config file should be a toml file"
    # path_to_exp,exp_name = prepare_videos(args.video_dir,args.camera_parameters,args.rotate,args.exp_name)
    # shutil.copyfile(args.config,os.path.join(path_to_exp,'Config.toml'))

    # if not (os.path.exists(os.path.join(path_to_exp,'pose')) and os.path.exists(os.path.join(path_to_exp,'pose_rotated'))):
    #     #pass
    #     execute_2d_detection(path_to_exp)
    #     rotate2dBack(os.path.join(path_to_exp,'pose'),args.camera_parameters)
    #     shutil.move(os.path.join(path_to_exp,'pose_rotated'), os.path.join(path_to_exp,'pose'))
    # #raise ValueError("Stop here")
    # os.makedirs(os.path.join(path_to_exp,'calibration'),exist_ok=True)
    # shutil.copyfile(args.camera_parameters,os.path.join(path_to_exp,'calibration','camera_parameters.qca.txt'))
    # execute_pose2sim_triangluation(path_to_exp,args.sync,args.marker_augmentation)
    # os.chdir(os.path.join(os.getcwd(),"../../"))
    # path_to_trc = glob.glob(os.path.join(path_to_exp,'pose-3d','*_filt_butterworth.trc'))[0]
    # if args.opensim:
    #     create_opensim(path_to_trc,exp_name)