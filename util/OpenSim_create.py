import argparse
import os
import xml.etree.ElementTree as ET

import opensim


def do_scaling(path_to_scaling):
    opensim.ScaleTool(path_to_scaling).run()
    print("Scaling has been completed")


def do_ik(path_to_ik_setup):
    opensim.InverseKinematicsTool(path_to_ik_setup).run()
    print("Inverse Kinematics has been completed")


def adapt_scaling_xml(
    setup_file,
    trc_file,
    time_range,
    output_dir,
    model_path,
):
    # Read the file
    tree = ET.parse(setup_file)
    root = tree.getroot()

    # Change path to the trc file
    for item in root.iter("marker_file"):
        item.text = trc_file

    # Change the time range
    for item in root.iter("time_range"):
        item.text = str(time_range[0]) + " " + str(time_range[1])

    # Change the output model file
    for item in root.iter("output_model_file"):
        item.text = os.path.abspath(
            os.path.join(output_dir, "scaled_model.osim")
        )

    for item in root.iter("model_file"):
        item.text = model_path

    # for item in root.iter('marker_set_file'):
    #     item.text = os.path.join(output_dir,'marker_set.xml')

    # Write the new file
    filename = os.path.basename(setup_file)
    outfile = os.path.join(output_dir, filename)
    tree.write(outfile)


def adapt_ik_xml(
        setup_file,
        trc_file,
        output_dir,
        time_range=None
    ):
    # Read the file
    tree = ET.parse(setup_file)
    root = tree.getroot()

    # Change path to the trc file
    for item in root.iter("marker_file"):
        item.text = trc_file

    # Change the time range
    if time_range is not None:
        for item in root.iter("time_range"):
            item.text = str(time_range[0]) + " " + str(time_range[1])
    # else:
    #     for item in root.iter("time_range"):
    #         item.text = " "

    for item in root.iter("output_motion_file"):
        item.text = os.path.abspath(os.path.join(output_dir, "ik.mot"))

    for item in root.iter("model_file"):
        item.text = os.path.join(output_dir, "scaled_model.osim")

    for item in root.iter("results_directory"):
        item.text = output_dir

    filename = os.path.basename(setup_file)
    tree.write(os.path.join(output_dir, filename))


def create_opensim(
    trc,
    experiment_dir,
    scaling_time_range=[0.5, 1.0],
    opensim_dir="./assets/opensim/Pose2Sim_Halpe26/",
    model="Model.osim",
    ik_file="IK_Setup.xml",
    scaling_file="Scaling_Setup.xml",
    ik_time_range=None,
):
    opensim_dir = os.path.join(experiment_dir, "..", "..", opensim_dir)

    model_path = os.path.join(opensim_dir, model)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")

    scaling_setup_file = os.path.join(opensim_dir, scaling_file)
    if not os.path.exists(scaling_setup_file):
        raise FileNotFoundError(f"Scaling file {scaling_setup_file} not found")

    ik_setup_path = os.path.join(opensim_dir, ik_file)
    if not os.path.exists(ik_setup_path):
        raise FileNotFoundError(f"IK file {ik_setup_path} not found")

    output_dir = os.path.join(experiment_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Scaling
    scaling_file = os.path.basename(scaling_file)
    adapt_scaling_xml(
        setup_file=scaling_setup_file,
        trc_file=trc,
        time_range=scaling_time_range,
        output_dir=output_dir,
        model_path=model_path,
    )
    do_scaling(os.path.join(output_dir, scaling_file))

    # Inverse Kinematics
    adapt_ik_xml(ik_setup_path, trc, output_dir, ik_time_range)
    do_ik(os.path.join(output_dir, ik_file))

    print("The results can be found in: ", output_dir)
    return (
        output_dir,
        os.path.join(output_dir, "ik.mot"),
        os.path.join(output_dir, "scaled_model.osim"),
    )


if __name__ == "__main__":
    """'
    !!!!!
    Caution: Some assumption especial when it comes to the path to the files are made that are platform dependent
    e.g the path to the files are assumed to be windows paths and the path seperator is assumed to be '\'
    !!!!!
    """
    parser = argparse.ArgumentParser(description="Create an InversKinematics calc")
    parser.add_argument(
        "--opensim_setup",
        type=str,
        default=r"./OpenSim",
        help="Root of the OpenSim setup",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=r"Model_Pose2Sim_Halpe26.osim",
        help="Path to the model file",
    )
    parser.add_argument(
        "--trc",
        type=str,
        required=True,
        help="Reative Path from project root to the trc file which is the result of the pos2sim triangulation",
    )
    parser.add_argument(
        "--ik_setup",
        type=str,
        default=r"Inverse-Kinematics\IK_Setup_Pose2Sim_Halpe26.xml",
        help="Path to the ik setup file, reltive from the root directory",
    )
    parser.add_argument(
        "--sclaing_setup",
        type=str,
        default=r"Scaling\Scaling_Setup_Pose2Sim_Halpe26.xml",
        help="Path to the scaling setup file relative to the root dirtectory",
    )
    parser.add_argument(
        "--scaling_time_range",
        type=list,
        default=[0.5, 1.0],
        help="Time range for the scaling, should be choosen carefully, choose time where person is streched/normal/T-Pose best would be a separte T pose for the scaling",
    )
    parser.add_argument(
        "--ik_time_range",
        type=list,
        default=None,
        help="Time range of seconds for the ik. Default None means every frame others e.g [0.0,1] mean each frame from 0 to 1s of the video ",
    )
    parser.add_argument(
        "--output", type=str, default=r"./output", help="Path to the output file"
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="default",
        help="Name of the experiment should be unique/not exist will be used for dir name...",
    )
    args = parser.parse_args()

    create_opensim(
        args.trc,
        args.experiment_name,
        args.scaling_time_range,
        args.opensim_setup,
        args.model,
        args.ik_setup,
        args.sclaing_setup,
        args.ik_time_range,
        args.output,
    )
