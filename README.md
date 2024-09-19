Pose2Sim setup for LIHS dataset
===============================
Cotains many util functions that are not needed directly in the main code, but could be useful for debugging and testing or some edge cases.

## Installation
Follow the instruction to install Pose2Sim in https://github.com/perfanalytics/pose2sim/tree/main?tab=readme-ov-file#2d-pose-estimation
Also install the opensim library(detailed in the above link)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

What files do you need?
1. Video file
2. The camera paramters file. LIHS has it in a similiar/eqaul format to QCA camera parameters format.
    !!!!!!!Code assumes this format.!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Attention!:
In the Lihs data set the view of the videos are Rotated, to have better 2d detection use util/rotator.py to rotate the videos.
After the 2d detection is done, doesnt matter external or internal, the 2d keypoints need to be rotated back to the original view. Use util/jsonMMPOSE_CMU.py for that.
## How to run the code?
### With new Pose2Sim code which inculeds the RTMPose 2d Detection
1. Create a new Experiment in the "Data/experiments" folder.
2. In the experiment folder add the video files in a folder called "videos" and the camera parameters in a file called calibrations.
3. Copy a config.toml file from Pose2Sim git or some from other experiments and modify it according to your needs.
3.1 Especially the "video" and "calibration" fields in the config.toml file and which 2d Pose Framework you want. E.g the video input format or if some graphs/2d poses should be visualized.
On some linux machine the visulaization might not work. In that case set the field to false.
4. Go into the Expirement folder e.g cd data/experiments/your_experiment
5. Run Pose2Sim_with_2d.py with apropriate arguments. !! NOTE on Windows some times premisson error on renaming folders. Just run the code again.
6. The resulting trinagulated 3d pose is save in pose-3d folder in the experiment folder.
7. To create OpenSim model from the 3d pose run .\util\OpenSim_create.py with the appropriate arguments. The scaled model and motion file is saved in the output folder.
8. Open OpenSim and load the model and motion file.

### With new Pose2Sim code which needs external 2d Pose Detection
1. Create a new Experiment in the experiments folder.
2. In the experiment folder add the detected 2d Keypoints in a folder called "pose" and the camera parameters in a file called calibrations.
3. In util are is file formater from alphapose format to openpose format which Pose2Sim supports.
4. If 2d points need rotation use util/rotate2dBack.py
5. Copy a config.toml file from Pose2Sim git or some from other experiments and modify it according to your needs.
6. Go into the Expirement folder e.g cd data/experiments/your_experiment and run Pose2SimP.py with apropriate arguments.
7. look at point 6-8 from the above section.


## Blender Visualization
1. Go to https://github.com/davidpagnon/Pose2Sim_Blender?tab=readme-ov-file
and follow instructions
2. If you did not do a full installation of the plugin or there are some error in importing the .mot file
see section "opensim-imports -> Import Motion" in https://github.com/davidpagnon/Pose2Sim_Blender?tab=readme-ov-file#opensim-imports

## Example execution for LIHS data
1. Select 3 videos from the LIHS dataset from the same experiment and put them into a seperate folder. E.g From ROM2 Generic Markerless 2_Miqus_1_23087.avi,Generic Markerless 2_Miqus_3_28984.avi,Generic Markerless 2_Miqus_6_28983.avi
2. Take the the camera calibration file and delete every camera expcept the 3 cameras for the selected videos. E.g In ROM2 the file Generic Markerless 2.settings.xml (For example the one in project root)
3. Take a look in the Config.toml in the project root. Change anyparameters that you want to change. E.g In which vile format the videos are. Right now if the videos are rotated such that the viewrotation is 0 (The case for LIHS), they are stored as MP4 files.
4. Run Pose2Sim_with_2d.py e.g python Pose2Sim_with_2d.py --camera_parameters "Path to the camera parameters" --rotate True --video_folder "Path to the video folder" --config "Path to the config.toml file can be the one from the project root"
5. NOTE right now the RTMPose 2d detection is set to lightweight/small in the config.toml file. If you want better results change it to balanced or performance.
