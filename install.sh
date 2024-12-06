conda create -n TracX python=3.9 -y
conda activate TracX
conda install -c opensim-org opensim -y
pip install .
pip install onnxruntime-gpu