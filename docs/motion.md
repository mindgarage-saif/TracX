# Estimating 3D Motion in TracX

This document describes the process of estimating 3D motion from 2D video data in TracX. The software uses a combination of 2D pose estimation and camera calibration to reconstruct 3D poses of human subjects, and is based on the Pose2Sim library.

## Prequisites

Before you can start estimating 3D motion, you need to have the following:
1. Synced video recordings of the subject from multiple cameras.
2. The camera paramters file in the Qualisys format (`.xml`).

The recordings can be obtained using the recording tool in TracX.

> [!WARNING]
> The camera calibration tool is not yet implemented in the current version of TracX. You need to calibrate the cameras using an external tool and provide the camera parameters file in the Qualisys format.

> [!TIP]
> In the LIHS dataset, many videos are rotated. For optimal 2D detection, use `util/rotator.py` to fix the videos. After the 2D detection is done, the keypoints need to be rotated back to the original view with `util/jsonMMPOSE_CMU.py`. This is also supported through the TracX UI.

## Usage

### 2D Pose Estimation

1. Create a new experiment in the `experiments/<experiment-name>` directory.
2. Add a `Config.toml` file to specify the experiment parameters. See this [example](https://github.com/perfanalytics/pose2sim/blob/main/Pose2Sim/Demo_SinglePerson/Config.toml) for reference.
3. Add the video files in a folder called `videos` and the camera parameters in a folder called `calibration`.

The folder structure should look like this:
    ```
    experiments/
    ├── <experiment-name>/
    |   ├── Config.toml
    │   ├── videos/
    │   │   ├── video1.mp4
    │   │   ├── video2.mp4
    │   │   └── video3.mp4
    │   └── calibration/
    │       └── camera_parameters.qca.txt
    └── ...
    ```

4. **(a) [Using Pose2Sim 2D Pose Estimation (RTMPose)] Configure the `Config.toml` file to specify the video input format and the 2D pose framework you want to use.  Then change the current directory to the experiment folder and run the `Pose2Sim_with_2D.py` script with the appropriate arguments.

> [!TIP]
> You can set the video input format and choose the graphs/2D poses to visualize.

> [!WARNING]
> On some Linux machines, the visualization might not work, so set the field to `false`.

4. **(b) [Using External 2D Pose Estimation] Add the detected 2D keypoints in a folder called `pose` under the experiment folder. Configure the `Config.toml` file to specify the 2D pose framework you used and any other parameters. Then change he current directory to the experiment folder and run the `Pose2SimP.py` script with the appropriate arguments.

### 3D Triangulation

The trinagulated 3d poses are saved in the `experiments/<experiment-name>/pose-3d` folder.

### Visualization

You can visualize the 3D poses in OpenSim or Blender.

#### OpenSim Visualization

To create OpenSim model from the 3d pose run `./util/OpenSim_create.py` with the appropriate arguments. This will create the following files:
- `scaled_model.osim`: OpenSim model file
- `ik.mot`: Motion file

You can then import these files into OpenSim for visualization.

#### Blender Visualization

To use Blender visualization, you need to install the Pose2Sim Blender plugin. Follow the instructions [here](https://github.com/davidpagnon/Pose2Sim_Blender?tab=readme-ov-file).

> [!NOTE]
> If you did not do a full installation of the plugin or there are some error in importing the `.mot` file, see "Import Motion" section [here](https://github.com/davidpagnon/Pose2Sim_Blender?tab=readme-ov-file#opensim-imports)

## Sample Workflow with LIHS Dataset

Here is a sample workflow to estimate 3D motion using the LIHS dataset:

1. Select 3 videos from the LIHS dataset from the same experiment and put them into a separate folder.

2. Copy the camera calibration file and delete all cameras except the 3 cameras for the selected videos. For example, in `ROM2`, the file `Generic Markerless 2.settings.xml`.
   ```
    |── ROM2/
    |   ├── calibration/
    |   |   └── Generic Markerless 2.settings.xml
    |   ...
    ```

3. Copy the example `Config.toml` file from the `assets/examples/Config.toml` to the experiment folder and modify the parameters as needed (e.g. video file format)

> [!TIP]
> The RTMPose 2D detection is set to `lightweight` in the sample `Config.toml` file. For better results, change it to `balanced` or `performance`.

The final folder structure should look like this:
    ```
    experiments/
    ├── ROM2/
    |   ├── Config.toml
    │   ├── videos/
    │   │   ├── Generic Markerless 2_Miqus_1_23087.avi
    │   │   ├── Generic Markerless 2_Miqus_3_28984.avi
    │   │   └── Generic Markerless 2_Miqus_6_28983.avi
    │   └── calibration/
    │       └── Generic Markerless 2.settings.xml
    └── ...
    ```

Run the following command to estimate 3D motion:

```bash
python Pose2Sim_with_2D.py \
--camera_parameters "Path to the camera parameters" \
--rotate True \
--video_folder "Path to the video folder" \
--config "Path to the config.toml file can be the one from the project root"
```
