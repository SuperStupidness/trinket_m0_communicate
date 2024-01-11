#!/bin/bash

# Script to compile python library into board with Circuitpython with mpy-cross
# and copy code.py to board
# Intended to work on Linux Debian Based system

# Change linux username to match what you are using
# If the board is located in a different folder, change it in dest
linuxusername=tan
dest=/media/${linuxusername}/CIRCUITPY/lib

localcopyflag=1
localmpycopy=./lib
pyfolder=./lib_python

# Compile python files to mpy
./mpy-cross ${pyfolder}/custom_fingerprint_lib.py
./mpy-cross ${pyfolder}/adafruit_fingerprint_reduced.py

# Copy code.py to board
cp -u code.py ${dest}/..

# Copy .mpy files to board's lib folder
cp -u ${pyfolder}/custom_fingerprint_lib.mpy $dest
cp -u ${pyfolder}/adafruit_fingerprint_reduced.mpy $dest

# Copy .mpy files to lib folder as a local copy
cp -u ${pyfolder}/custom_fingerprint_lib.mpy $localmpycopy
cp -u ${pyfolder}/adafruit_fingerprint_reduced.mpy $localmpycopy

# Remove compiled python file in lib_python
rm ${pyfolder}/custom_fingerprint_lib.mpy ${pyfolder}/adafruit_fingerprint_reduced.mpy
