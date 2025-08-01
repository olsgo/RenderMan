# RenderMan Debug Guide

```
       ______               _          ___  ___
       | ___ \             | |         |  \/  |
       | |_/ /___ _ __   __| | ___ _ __| .  . | __ _ _ __
       |    // _ \ '_ \ / _` |/ _ \ '__| |\/| |/ _` | '_ \
       | |\ \  __/ | | | (_| |  __/ |  | |  | | (_| | | | |
       \_| \_\___|_| |_|\__,_|\___|_|  \_|  |_/\__,_|_| |_|

* *  Command Line VSTi Audio, Features and Parameter Renderer  * *
```

This document provides comprehensive debugging information for RenderMan developers and users encountering issues with the VST host, Python bindings, audio rendering, or build processes.

## Table of Contents

1. [Quick Debugging Checklist](#quick-debugging-checklist)
2. [Build System Debugging](#build-system-debugging)
3. [Plugin Loading Issues](#plugin-loading-issues)
4. [Python Import and Binding Problems](#python-import-and-binding-problems)
5. [Audio Rendering Debugging](#audio-rendering-debugging)
6. [Parameter and Patch Issues](#parameter-and-patch-issues)
7. [Platform-Specific Debugging](#platform-specific-debugging)
8. [Development and Testing Tools](#development-and-testing-tools)
9. [Performance Debugging](#performance-debugging)
10. [Troubleshooting Common Errors](#troubleshooting-common-errors)

## Quick Debugging Checklist

Before diving into detailed debugging, run through this quick checklist:

### ✅ Environment Check
```bash
# Check your platform and architecture
uname -a

# Verify Python version (3.12+ recommended)
python3 --version

# Check if librenderman.so exists
ls -la librenderman.so*

# Quick import test
python3 -c "import librenderman as rm; print('✅ RenderMan imported successfully')"
```

### ✅ Build Status Check
```bash
# Linux
cd Builds/LinuxMakefile && ls -la build/

# macOS  
cd Builds/MacOSX && ls -la build/Debug/ build/Release/

# Windows
cd Builds/VisualStudio2019 && dir
```

## Build System Debugging

### JUCE/Projucer Issues

RenderMan uses JUCE as its audio framework. Common build issues:

**Problem**: Projucer regeneration breaks custom settings
```bash
# Solution: Always backup the .jucer files before regeneration
cp RenderMan.jucer RenderMan.jucer.backup
```

**Problem**: Missing JUCE modules
```bash
# Check if JUCE modules are present
ls -la JuceLibraryCode/modules/

# Verify key modules exist:
# - juce_core, juce_audio_devices, juce_audio_formats
# - juce_audio_processors, juce_audio_utils
```

### Linux Build Debugging

```bash
# Install missing dependencies
sudo apt-get update
sudo apt-get install -y \
    libboost-all-dev \
    libfreetype6-dev \
    libx11-dev \
    libxinerama-dev \
    libxrandr-dev \
    libxcursor-dev \
    mesa-common-dev \
    libasound2-dev \
    freeglut3-dev \
    libxcomposite-dev \
    libcurl4-gnutls-dev

# Check boost python specifically
dpkg -l | grep boost-python
# or
pkg-config --libs python3

# Build with verbose output
cd Builds/LinuxMakefile
make VERBOSE=1
```

**Debug Makefile Issues**:
```bash
# Check Python configuration
python3-config --includes --ldflags --libs

# Verify boost libraries
ldconfig -p | grep boost_python
```

### macOS Build Debugging

For M1 Max/Apple Silicon, see [BUILD_INSTRUCTIONS_M1_SEQUOIA.md](BUILD_INSTRUCTIONS_M1_SEQUOIA.md).

```bash
# Check Homebrew dependencies
brew list | grep -E "(boost|python)"

# Verify Xcode tools
xcode-select --print-path
xcodebuild -version

# Check architecture settings
lipo -info Builds/MacOSX/build/Debug/librenderman.so.dylib

# M1 specific: Check for correct boost version
ls /opt/homebrew/lib/libboost_python*
```

**Common M1 Issues**:
```bash
# Architecture mismatch
# Solution: Ensure ARCHS = "arm64 x86_64" in project settings

# Boost not found
# Solution: Create symlink if needed
cd /opt/homebrew/lib
ln -s libboost_python311.dylib libboost_python312.dylib
```

### Windows Build Debugging

```cmd
REM Check Visual Studio version compatibility
echo %VisualStudioVersion%

REM Verify boost installation
dir C:\Boost\lib\libboost_python*

REM Check Python paths
python -c "import sysconfig; print(sysconfig.get_path('include'))"
```

## Plugin Loading Issues

### VST Plugin Path Problems

RenderMan supports various plugin formats (.vst, .vst3, .au, .so). Common issues:

```python
import librenderman as rm

# Initialize with debug output
engine = rm.RenderEngine(44100, 512, 512)

# Test plugin discovery
try:
    plugins_xml = engine.get_available_plugins_xml("/path/to/plugins/")
    print("Available plugins:", plugins_xml)
except Exception as e:
    print("Plugin discovery failed:", e)
```

**Debug Plugin Loading**:
```python
# Get detailed plugin information
plugin_names = engine.get_available_plugin_names("/path/to/plugins/")
print("Found plugins:", plugin_names)

# Try loading with index
success = engine.load_plugin("/path/to/plugin.vst", 0)
if not success:
    print("❌ Plugin loading failed - check plugin path and format")
```

### Common Plugin Loading Errors

1. **"RenderEngine::loadPlugin error: plugin index X provided, but only Y plugins detected"**
   - Solution: Check plugin index is within bounds
   - Use `get_available_plugin_names()` to see available indices

2. **"jassert (pluginDescriptions.size() > 0)"**
   - Plugin format not supported or plugin corrupted
   - Check plugin file permissions and format

3. **Plugin loads but produces no audio**
   - Check plugin requires MIDI input
   - Verify sample rate and buffer size compatibility

### Plugin Format Support

```cpp
// In RenderEngine.cpp, these formats are automatically added:
// - VST2 (.vst, .dll)
// - VST3 (.vst3)  
// - AudioUnit (.component, .au) [macOS only]
// - LADSPA (.so) [Linux only]
```

## Python Import and Binding Problems

### Import Failures

**Error**: `ImportError: No module named 'librenderman'`
```bash
# Check if library exists in current directory
ls -la librenderman.so*

# Verify Python can find the module
export PYTHONPATH="${PYTHONPATH}:/path/to/renderman/build"
python3 -c "import librenderman"
```

**Error**: `ImportError: dynamic module does not define module export function`
```bash
# Check library architecture matches Python
file librenderman.so
python3 -c "import platform; print(platform.machine())"

# Verify boost python version compatibility
ldd librenderman.so | grep boost_python
```

### Boost.Python Version Mismatches

```bash
# Check boost python version
pkg-config --modversion boost_python3-3.12
# or
python3 -c "import sysconfig; print(sysconfig.get_config_var('VERSION'))"

# Update library links if needed (Linux)
sudo ldconfig

# macOS: Check dynamic library dependencies
otool -L librenderman.so
```

### Python API Debugging

```python
import librenderman as rm

# Test basic functionality
try:
    engine = rm.RenderEngine(44100, 512, 512)
    print("✅ RenderEngine created successfully")
    
    # Test parameter access
    size = engine.get_plugin_parameter_size()
    print(f"Plugin parameters: {size}")
    
except Exception as e:
    print(f"❌ API Error: {e}")
    import traceback
    traceback.print_exc()
```

## Audio Rendering Debugging

### No Audio Output

```python
import librenderman as rm

engine = rm.RenderEngine(44100, 512, 512)
success = engine.load_plugin("/path/to/synth.vst")

if success:
    # Test basic rendering
    engine.render_patch(60, 100, 1.0, 2.0)  # C4, velocity 100, 1s note, 2s total
    
    # Check audio frames
    audio = engine.get_audio_frames()
    print(f"Audio frames generated: {len(audio)}")
    
    if len(audio) == 0:
        print("❌ No audio generated - check:")
        print("  - Plugin requires MIDI input")
        print("  - Plugin parameters are set correctly")
        print("  - Note length and render length are > 0")
```

### Audio Quality Issues

```python
# Check RMS levels
rms_frames = engine.get_rms_frames()
if rms_frames:
    max_rms = max(rms_frames)
    print(f"Peak RMS: {max_rms}")
    if max_rms < 0.001:
        print("⚠️  Very quiet audio - check gain parameters")
    elif max_rms > 0.9:
        print("⚠️  Possible clipping - check levels")
```

### MFCC Feature Extraction Debug

```python
# Test MFCC extraction
mfcc_frames = engine.get_mfcc_frames()
print(f"MFCC frames: {len(mfcc_frames)}")

if mfcc_frames:
    first_frame = mfcc_frames[0]
    print(f"MFCC coefficients per frame: {len(first_frame)}")
    print(f"First frame: {first_frame}")
else:
    print("❌ No MFCC data - check audio rendering")
```

## Parameter and Patch Issues

### Parameter Range Problems

```python
# Get parameter descriptions
params = engine.get_plugin_parameters_description()
for i, (param_id, param_name) in enumerate(params):
    print(f"Parameter {i}: {param_name} (ID: {param_id})")
```

### Patch Setting Debug

```python
# Test parameter setting
patch = [(0, 0.5), (1, 0.8)]  # Set first param to 0.5, second to 0.8

try:
    engine.set_patch(patch)
    print("✅ Patch set successfully")
    
    # Verify patch was applied
    current_patch = engine.get_patch()
    print("Current patch:", current_patch)
    
except Exception as e:
    print(f"❌ Patch setting failed: {e}")
```

### Parameter Override Testing

```python
# Test parameter override
success = engine.override_plugin_parameter(0, 0.75)
if success:
    print("✅ Parameter override successful")
else:
    print("❌ Parameter override failed - check parameter index")

# Remove override
engine.remove_overriden_plugin_parameter(0)
```

## Platform-Specific Debugging

### Linux-Specific Issues

```bash
# Check audio system
aplay -l
# or
pulseaudio --check

# ALSA debugging
cat /proc/asound/cards

# Library dependencies
ldd librenderman.so | grep -E "(not found|boost|python)"
```

### macOS-Specific Issues

```bash
# Check Core Audio
system_profiler SPAudioDataType

# Security/permissions (for plugin scanning)
csrutil status

# Library paths
echo $DYLD_LIBRARY_PATH
otool -L librenderman.so
```

### Windows-Specific Issues

```cmd
REM Check audio devices
dxdiag /t dxdiag_output.txt

REM Dependency walker for DLL issues
REM Use Dependency Walker (depends.exe) to check DLL dependencies
```

## Development and Testing Tools

### Test Script Template

Create a debug test script:

```python
#!/usr/bin/env python3
"""RenderMan Debug Test Script"""

import os
import sys
import traceback

def test_import():
    """Test basic import"""
    try:
        import librenderman as rm
        print("✅ Import successful")
        return rm
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return None

def test_engine_creation(rm):
    """Test engine creation"""
    try:
        engine = rm.RenderEngine(44100, 512, 512)
        print("✅ Engine creation successful")
        return engine
    except Exception as e:
        print(f"❌ Engine creation failed: {e}")
        traceback.print_exc()
        return None

def test_plugin_discovery(engine, plugin_path):
    """Test plugin discovery"""
    try:
        plugins = engine.get_available_plugin_names(plugin_path)
        print(f"✅ Found {len(plugins)} plugins")
        for name, index in plugins.items():
            print(f"  {index}: {name}")
        return plugins
    except Exception as e:
        print(f"❌ Plugin discovery failed: {e}")
        return {}

def main():
    plugin_path = sys.argv[1] if len(sys.argv) > 1 else "/usr/lib/vst"
    
    print("RenderMan Debug Test")
    print("=" * 40)
    
    rm = test_import()
    if not rm:
        return 1
    
    engine = test_engine_creation(rm)
    if not engine:
        return 1
    
    plugins = test_plugin_discovery(engine, plugin_path)
    if not plugins:
        print("⚠️  No plugins found - check plugin path")
    
    print("Debug test complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Build Verification

Use the provided verification script:
```bash
# For M1 Mac users
python3 verify_m1_build.py

# General verification
python3 debug_test.py /path/to/vst/plugins
```

## Performance Debugging

### Memory Usage

```python
import psutil
import librenderman as rm

# Monitor memory during rendering
process = psutil.Process()
print(f"Initial memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")

engine = rm.RenderEngine(44100, 512, 512)
engine.load_plugin("/path/to/plugin.vst")

print(f"After loading: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Render multiple patches and monitor memory
for i in range(10):
    engine.render_patch(60, 100, 1.0, 2.0)
    if i % 2 == 0:
        print(f"After {i+1} renders: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Timing Analysis

```python
import time
import librenderman as rm

engine = rm.RenderEngine(44100, 512, 512)
engine.load_plugin("/path/to/plugin.vst")

# Time rendering
start_time = time.time()
engine.render_patch(60, 100, 1.0, 5.0)
render_time = time.time() - start_time

print(f"Rendering 5s audio took: {render_time:.3f}s")
print(f"Real-time factor: {5.0/render_time:.1f}x")
```

## Troubleshooting Common Errors

### "Symbol not found" Errors

```bash
# Check library symbols (Linux)
nm -D librenderman.so | grep -i python

# macOS  
nm -g librenderman.so | grep -i python

# Verify boost python symbols
nm -D /usr/lib/libboost_python*.so | grep init_module
```

### Segmentation Faults

```bash
# Run with debugger
gdb --args python3 -c "import librenderman"
# In gdb:
# (gdb) run
# (gdb) bt  # for backtrace when crash occurs

# Valgrind for memory issues (Linux)
valgrind --leak-check=full python3 debug_test.py
```

### Plugin Crashes

```python
# Wrap plugin operations in try-catch
try:
    engine.load_plugin(plugin_path)
    engine.render_patch(60, 100, 1.0, 2.0)
except Exception as e:
    print(f"Plugin operation failed: {e}")
    # Try with different buffer sizes
    engine2 = rm.RenderEngine(44100, 256, 256)  # Smaller buffers
```

### Threading Issues

RenderMan is not thread-safe. Ensure single-threaded usage:

```python
# ❌ Don't do this
import threading
engine = rm.RenderEngine(44100, 512, 512)

def render_thread():
    engine.render_patch(60, 100, 1.0, 2.0)

threading.Thread(target=render_thread).start()  # Unsafe!

# ✅ Do this instead
# Use separate engine instances per thread or use locks
```

## Getting Help

If debugging doesn't resolve your issue:

1. **Check the GitHub Issues**: [RenderMan Issues](https://github.com/fedden/RenderMan/issues)
2. **JUCE Forums**: For JUCE-related problems
3. **Boost Documentation**: For Boost.Python issues
4. **Create a Minimal Reproduction**: Strip down to simplest failing case

When reporting issues, include:
- Platform and architecture
- Python version  
- Boost version
- Build configuration (Debug/Release)
- Minimal code to reproduce
- Complete error messages and stack traces
- Output from debug verification scripts

## Debug Build Configuration

For development, enable debug builds:

```bash
# Linux
cd Builds/LinuxMakefile
make CONFIG=Debug

# macOS
# In Xcode, select Debug scheme

# Add debug symbols and verbose output
# Edit Makefile to add: -g -DDEBUG -v
```

---

*This debug guide is maintained alongside RenderMan. For updates and additional debugging information, see the main README.md and platform-specific build instructions.*