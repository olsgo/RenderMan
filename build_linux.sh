#!/bin/bash
# Quick build script for RenderMan with Python 3.12

set -e

echo "Building RenderMan with Python 3.12 support..."

cd Builds/LinuxMakefile

# Update the build to use Python 3.12 and boost_python312
# Add -Wno-error to ignore warnings that are treated as errors
make CONFIG=Debug \
  CPPFLAGS="-I/usr/include/python3.12 -I/usr/include/python3.12/cpython -Wno-error" \
  CXXFLAGS="-Wno-error" \
  LDFLAGS="-lpython3.12 -lboost_python312" \
  V=1

echo "Build complete! Library should be at: Builds/LinuxMakefile/build/librenderman.so"