import opensim
import os
import argparse
import xml.etree.ElementTree as ET

def do_scaling(path_to_scaling):
    opensim.ScaleTool(path_to_scaling).run()
    print('Scaling has been completed')

def do_ik(path_to_ik_setup):
    opensim.InverseKinematicsTool(path_to_ik_setup).run()
    print('Inverse Kinematics has been completed')

def addapt_scaling_xml(path_to_scaling,trc_file,scaling_time_range,output_dir,model_file_path):
    tree = ET.parse(path_to_scaling)
    root = tree.getroot()
    for marker_file in root.iter('marker_file'):
        marker_file.text = trc_file # might need to be changed for linux because ther it is / instead of \
    for time_range in root.iter('time_range'):
        time_range.text = str(scaling_time_range[0]) + ' ' + str(scaling_time_range[1])
    for output_model_file in root.iter('output_model_file'):
        output_model_file.text = os.path.join(output_dir,'scaled_model.osim')
    for model_file in root.iter('model_file'):
        model_file.text = model_file_path
    # for marker_set_file in root.iter('marker_set_file'):
    #     marker_set_file.text = os.path.join(output_dir,'marker_set.xml')
    tree.write(os.path.join(output_dir,path_to_scaling.split('\\')[-1]))

def addapt_ik_xml(path_to_ik_setup,trc_file,output_dir,ik_time_range=None):
    tree = ET.parse(path_to_ik_setup)
    root = tree.getroot()
    for marker_file in root.iter('marker_file'):
        marker_file.text = trc_file
    if ik_time_range is None:
        for time_range in root.iter('time_range'):
            time_range.text = ' '
    else:
        for time_range in root.iter('time_range'):
            time_range.text = str(ik_time_range[0]) + ' ' + str(ik_time_range[1])
    for output_motion_file in root.iter('output_motion_file'):
        output_motion_file.text = os.path.join(output_dir,'ik.mot')
    for model_file in root.iter('model_file'):
        model_file.text = os.path.join(output_dir,'scaled_model.osim')
    for results_directory in root.iter('results_directory'):
        results_directory.text = output_dir
    tree.write(os.path.join(output_dir,path_to_ik_setup.split('\\')[-1]))
if __name__ == '__main__':
    ''''
    !!!!!
    Caution: Some assumption especial when it comes to the path to the files are made that are platform dependent
    e.g the path to the files are assumed to be windows paths and the path seperator is assumed to be '\'
    !!!!!
    '''
    parser = argparse.ArgumentParser(description='Create an InversKinematics calc')
    parser.add_argument('--root', type=str, default=r"./OpenSim", help='Root of the OpenSim setup')
    parser.add_argument('--model', type=str, default=r"Model_Pose2Sim_Halpe26.osim", help='Path to the model file')
    parser.add_argument('--trc', type=str, default=r".\Data\experiments\new\LIHS\ROM2\pose-3d\ROM2_0-314_filt_butterworth.trc", help='Reative Path from project root to the trc file which is the result of the pos2sim triangulation')
    parser.add_argument('--ik_setup', type=str, default=r"Inverse-Kinematics\IK_Setup_Pose2Sim_Halpe26.xml", help='Path to the ik setup file, reltive from the root directory')
    parser.add_argument('--sclaing_setup', type=str, default=r"Scaling\Scaling_Setup_Pose2Sim_Halpe26.xml", help='Path to the scaling setup file relative to the root dirtectory')
    parser.add_argument('--scaling_time_range', type=list, default=[0.5,1.0], help='Time range for the scaling, should be choosen carefully, choose time where person is streched/normal/T-Pose best would be a separte T pose for the scaling')
    parser.add_argument('--ik_time_range', type=list, default=None, help='Time range of seconds for the ik. Default None means every frame others e.g [0.0,1] mean each frame from 0 to 1s of the video ')
    parser.add_argument('--output', type=str, default=r"./output", help='Path to the output file')
    parser.add_argument('--experiment_name', type=str, default='default', help='Name of the experiment should be unique/not exist will be used for dir name...')
    args = parser.parse_args()
    model_path = os.path.join(args.root,args.model)
    args.model = model_path
    os.makedirs(args.output,exist_ok=True)
    scaling_path = os.path.join(args.root,args.sclaing_setup)
    args.sclaing_setup = scaling_path
    ik_path = os.path.join(args.root,args.ik_setup)
    args.ik_setup = ik_path
    # do the scaling
    addapt_scaling_xml(args.sclaing_setup,args.trc,args.scaling_time_range,args.output,args.model)
    do_scaling(os.path.join(args.output,args.sclaing_setup.split('\\')[-1]))
    
    # do the ik
    addapt_ik_xml(args.ik_setup,args.trc,args.output,args.ik_time_range)
    do_ik(os.path.join(args.output,args.ik_setup.split('\\')[-1]))
    print('Inverse Kinematics has been completed')
    print('The results can be found in: ',args.output)