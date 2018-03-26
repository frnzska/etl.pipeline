#!/usr/bin/env bash

FCT_NAME=$2
ZIP_FOLDER=$FCT_NAME.zip


echo "create build directory"
mkdir build_dir

echo "install dependencies "
if [ -f "requirements.txt" ]; then pip install -Ur "requirements.txt" -t build_dir; fi;

echo "copy source code"
cp lambda_function.py build_dir/lambda_function.py

echo "zip all"
cd build_dir && zip -r $ZIP_FOLDER .
