import os
from Pose2Sim import Pose2Sim
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

if __name__ == '__main__':
    argspaser = argparse.ArgumentParser()
    argspaser.add_argument("--path",default=r".\Data\experiments\old\LIHS\ROM2\Config.toml", type=str, help="Path to the config file")
    argspaser.add_argument("--sync",default=False, type=bool, help="Sync the data")
    argspaser.add_argument("--marker_augmentation",default=False, type=bool, help="Marker augmentation")
    args = argspaser.parse_args()
    execute_pose2sim_triangluation(args.path,args.sync,args.marker_augmentation)