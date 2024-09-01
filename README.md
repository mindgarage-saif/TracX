Pose2Sim setup for LIHS dataset
===============================
Cotains many util functions that are not needed directly in the main code, but could be useful for debugging and testing or some edge cases.

## Installation
Follow the instruction to install Pose2Sim in https://github.com/perfanalytics/pose2sim/tree/main?tab=readme-ov-file#2d-pose-estimation
Also install the opensim library(detailed in the above link)

What files do you need?
1. Video file
2. The camera paramters file. LIHS has it in a similiar/eqaul format to QCA camera parameters format.Code Assume this format.

Attention!:
In the Lihs data set the view of the videos are Rotated to have better 2d detection use util/rotator.py to rotate the videos.
After the 2d detection is done, doesnt matter external or internal, the 2d keypoints need to be rotated back to the original view. Use util/jsonMMPOSE_CMU.py for that.
## How to run the code?
### With new Pose2Sim code which inculeds the RTMPose 2d Detection
1. Create a new Experiment in the experiments folder.
2. In the experiment folder add the video files in a folder called "videos" and the camera parameters in a file called calibrations.
3. Copy a config.toml file from Pose2Sim git or some from other experiments and modify it according to your needs.
3.1 Especially the "video" and "calibration" fields in the config.toml file and which 2d Pose Framework you want. E.g the video input format or if some graphs/2d poses should be visualized.
On sime linux machine the visulaization might not work. In that case set the field to false.
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