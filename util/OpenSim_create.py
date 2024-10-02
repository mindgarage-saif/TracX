import opensim
import os
import argparse
import xml.etree.ElementTree as ET
from distutils.dir_util import copy_tree
import locale
def do_scaling(path_to_scaling):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    opensim.ScaleTool(path_to_scaling).run()
    print('Scaling has been completed')

def do_ik(path_to_ik_setup):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    opensim.InverseKinematicsTool(path_to_ik_setup).run()
    print('Inverse Kinematics has been completed')

def addapt_scaling_xml(path_to_scaling,sclaing_setup,trc_file,scaling_time_range,output_dir,model_file_path):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    tree = ET.parse(path_to_scaling)
    root = tree.getroot()
    for marker_file in root.iter('marker_file'):
        marker_file.text = trc_file # might need to be changed for linux because ther it is / instead of \
    for time_range in root.iter('time_range'):
        time_range.text = str(scaling_time_range[0]) + ' ' + str(scaling_time_range[1])
    for output_model_file in root.iter('output_model_file'):
        output_model_file.text = os.path.abspath(os.path.join(output_dir,'scaled_model.osim'))
    for model_file in root.iter('model_file'):
        model_file.text = model_file_path
    # for marker_set_file in root.iter('marker_set_file'):
    #     marker_set_file.text = os.path.join(output_dir,'marker_set.xml')
    print(os.path.join(output_dir,sclaing_setup))
    tree.write(os.path.join(output_dir,sclaing_setup))

def addapt_ik_xml(path_to_ik_setup,ik_setup,trc_file,output_dir,ik_time_range=None):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
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
        output_motion_file.text = os.path.abspath(os.path.join(output_dir,'ik.mot'))
    for model_file in root.iter('model_file'):
        model_file.text = os.path.join(output_dir,'scaled_model.osim')
    for results_directory in root.iter('results_directory'):
        results_directory.text = output_dir
    tree.write(os.path.join(output_dir,ik_setup))

def create_opensim(trc,experiment_name,scaling_time_range=[0.5,1.0],opensim_setup="./OpenSim",model = "Model_Pose2Sim_Halpe26.osim" ,ik_setup="Inverse-Kinematics/IK_Setup_Pose2Sim_Halpe26.xml",sclaing_setup="Scaling/Scaling_Setup_Pose2Sim_Halpe26.xml",ik_time_range=None,output="./output"):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    model_path = os.path.join(opensim_setup,model)
    model = model_path
    model = os.path.abspath(model)
    output = os.path.join('./experiments',experiment_name)
    os.makedirs(output,exist_ok=True)
    copy_tree(os.path.join(opensim_setup,'Geometry'),os.path.join(output,'Geometry'))
    scaling_path = os.path.join(opensim_setup,sclaing_setup)
    ik_path = os.path.join(opensim_setup,ik_setup)
    sclaing_setup = os.path.basename(sclaing_setup)
    ik_setup = os.path.basename(ik_setup)
    # do the scaling
    addapt_scaling_xml(scaling_path,sclaing_setup,trc,scaling_time_range,output,model)
    do_scaling(os.path.join(output,sclaing_setup))
    
    # do the ik
    addapt_ik_xml(ik_path,ik_setup,trc,output,ik_time_range)
    do_ik(os.path.join(output,ik_setup))
    print('Inverse Kinematics has been completed')
    print('The results can be found in: ',output)
    return output,os.path.join(output,'ik.mot'),os.path.join(output,'scaled_model.osim')
if __name__ == '__main__':
    ''''
    !!!!!
    Caution: Some assumption especial when it comes to the path to the files are made that are platform dependent
    e.g the path to the files are assumed to be windows paths and the path seperator is assumed to be '\'
    !!!!!
    '''
    parser = argparse.ArgumentParser(description='Create an InversKinematics calc')
    parser.add_argument('--opensim_setup', type=str, default=r"./OpenSim", help='Root of the OpenSim setup')
    parser.add_argument('--model', type=str, default=r"Model_Pose2Sim_Halpe26.osim", help='Path to the model file')
    parser.add_argument('--trc', type=str,required=True, help='Reative Path from project root to the trc file which is the result of the pos2sim triangulation')
    parser.add_argument('--ik_setup', type=str, default=r"Inverse-Kinematics\IK_Setup_Pose2Sim_Halpe26.xml", help='Path to the ik setup file, reltive from the root directory')
    parser.add_argument('--sclaing_setup', type=str, default=r"Scaling\Scaling_Setup_Pose2Sim_Halpe26.xml", help='Path to the scaling setup file relative to the root dirtectory')
    parser.add_argument('--scaling_time_range', type=list, default=[0.5,1.0], help='Time range for the scaling, should be choosen carefully, choose time where person is streched/normal/T-Pose best would be a separte T pose for the scaling')
    parser.add_argument('--ik_time_range', type=list, default=None, help='Time range of seconds for the ik. Default None means every frame others e.g [0.0,1] mean each frame from 0 to 1s of the video ')
    parser.add_argument('--output', type=str, default=r"./output", help='Path to the output file')
    parser.add_argument('--experiment_name', type=str, default='default', help='Name of the experiment should be unique/not exist will be used for dir name...')
    args = parser.parse_args()

    create_opensim(args.trc,args.experiment_name,args.scaling_time_range,args.opensim_setup,args.model,args.ik_setup,args.sclaing_setup,args.ik_time_range,args.output)