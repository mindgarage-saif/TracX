conda activate TracX
pip install -U pyinstaller

pyinstaller --noconfirm main.py
mkdir -p ./dist/main/_internal/aitviewer
wget https://raw.githubusercontent.com/eth-ait/aitviewer/refs/heads/main/aitviewer/aitvconfig.yaml -O ./dist/main/_internal/aitviewer/aitvconfig.yaml
cp -R ./assets ./dist/main/_internal
mkdir ./dist/main/_internal/Pose2Sim
cp -R ./Pose2Sim/OpenSim_Setup/ ./dist/main/_internal/Pose2Sim
mv ./dist/main/main ./dist/main/tracx

cp -R ./build_utils/AppDir/ ./dist/
mkdir -p ./dist/AppDir/usr
mv ./dist/main ./dist/AppDir/usr/bin

