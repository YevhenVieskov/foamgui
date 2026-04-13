#!/bin/bash
mkdir build && cd build
cmake .. -DPFUNIT_DIR=/path/to/pfunit/install
make
ctest --output-on-failure