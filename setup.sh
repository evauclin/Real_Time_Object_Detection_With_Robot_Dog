#!/usr/bin/bash
sudo apt-get update && sudo apt-get -y install protobuf-compiler
pushd Tensorflow/models/research
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .
python -m pip install .
popd

# pushd Tensorflow/protoc
# wget https://github.com/protocolbuffers/protobuf/releases/download/v3.15.6/protoc-3.15.6-linux-x86_32.zip
# unzip protoc-3.15.6-linux-x86_32.zip
# export PATH=`pwd`/bin:$PATH
# popd

pushd Tensorflow/models/research
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .
python setup.py build
sudo python setup.py install
cd slim
pip install -e .

# Install tflite
sudo apt-get install -y libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime
