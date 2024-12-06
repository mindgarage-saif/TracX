pip install -U pyinstaller

pyinstaller main.py
cp -R ./assets ./dist/main
mkdir ./dist/main/TracX
mkdir ./dist/main/Pose2Sim
cp -R ./Pose2Sim/OpenSim_Setup/ ./dist/main/Pose2Sim
