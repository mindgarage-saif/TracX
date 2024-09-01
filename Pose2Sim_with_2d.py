import os
from Pose2Sim import Pose2Sim
import argparse
from util.rotate2dBack import *
import argparse
def execute_pose2sim_triangluation(path,should_sync = False, with_marker_augmentation = False):
    Pose2Sim.calibration(path)
    Pose2Sim.personAssociation(path)
    if should_sync:
        Pose2Sim.synchronization()
    Pose2Sim.triangulation(path)
    Pose2Sim.filtering(path)
    if with_marker_augmentation:
        Pose2Sim.markerAugmentation(path)
def execute_2d_detection():
    Pose2Sim.poseEstimation()
if __name__ == '__main__':
    argspaser = argparse.ArgumentParser()
    argspaser.add_argument("--path",default=r"E:\Uni\MonocularSystems\HiWi\Data\experiments\new\LIHS\ROM2", type=str, help="Path to the config file")
    argspaser.add_argument("--sync",default=False, type=bool, help="Sync the data")
    argspaser.add_argument("--marker_augmentation",default=False, type=bool, help="Marker augmentation")
    argspaser.add_argument("--xml_camer_path",default=r"E:\Uni\MonocularSystems\HiWi\Gait Markerless 2.settings_new.xml", type=str, help="Path to the camera XML file")
    args = argspaser.parse_args()
    #execute_2d_detection()
    if not (os.path.exists(os.path.join(args.path,'pose')) and os.path.exists(os.path.join(args.path,'pose_rotated'))):
        execute_2d_detection()
        rotate2dBack(os.path.join(args.path,'pose'),args.xml_camer_path)
        os.rename(os.path.join(args.path,'pose_rotated'), os.path.join(args.path,'pose'))
    execute_pose2sim_triangluation(args.path,args.sync,args.marker_augmentation)