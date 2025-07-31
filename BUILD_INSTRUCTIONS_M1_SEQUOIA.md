# M1 Max / macOS Sequoia Build Instructions

This document outlines the changes made to ensure RenderMan builds successfully on Apple Silicon (M1 Max) with macOS Sequoia and Xcode.

## Changes Made for M1 Max / Sequoia Compatibility

### 1. Architecture Support
- Updated XCode project to build Universal Binaries (arm64 + x86_64)
- Changed `ARCHS = "$(NATIVE_ARCH_ACTUAL)"` to `ARCHS = "arm64 x86_64"`

### 2. Python Configuration Updates
- Updated from Python 2.7/3.8 to Python 3.12
- Changed library references:
  - `-lpython3.8` → `-lpython3.12`
  - `-lboost_python38` → `-lboost_python312`

### 3. Path Configuration
- Added Homebrew paths for M1 Mac support:
  - Header paths: `/opt/homebrew/include/python3.12`
  - Library paths: `/opt/homebrew/lib/python3.12/config-3.12-darwin`
- Updated header search paths to include both Intel and ARM locations

### 4. macOS SDK Updates
- Updated deployment target from macOS 10.9 to macOS 14.0 (Sequoia)
- Ensures compatibility with modern Xcode and macOS Sequoia

## Prerequisites for Building on M1 Max / Sequoia

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python 3.12
```bash
brew install python@3.12
```

### 3. Install Boost with Python 3.12 support
```bash
brew install boost-python3
```

Note: The Boost Python library should be named `boost_python312` for Python 3.12. If not available, you may need to:
```bash
# Check available boost python libraries
ls /opt/homebrew/lib/libboost_python*

# If needed, create a symlink for the correct version
cd /opt/homebrew/lib
ln -s libboost_python311.dylib libboost_python312.dylib  # adjust version as needed
```

### 4. Install Xcode Command Line Tools
```bash
xcode-select --install
```

## Building the Project

1. Open the XCode project:
   ```bash
   open Builds/MacOSX/RenderMan.xcodeproj
   ```

2. In Xcode:
   - Select your desired scheme (Debug or Release)
   - Choose "Any Mac" or "My Mac" as the destination
   - Build the project (⌘+B)

3. After successful build, the library will be located in:
   ```
   Builds/MacOSX/build/Debug/librenderman.so.dylib
   ```
   or
   ```
   Builds/MacOSX/build/Release/librenderman.so.dylib
   ```

4. Rename the output file for Python import:
   ```bash
   cd Builds/MacOSX/build/Debug  # or Release
   mv librenderman.so.dylib librenderman.so
   ```

## Updated Files

The following files were modified for M1 Max / Sequoia compatibility:

1. **RenderMan.jucer** - Updated Python paths and architecture settings
2. **RenderMan-py36.jucer** - Updated Python paths and architecture settings  
3. **Builds/MacOSX/RenderMan.xcodeproj/project.pbxproj** - Updated XCode project configuration

## Verification

To verify the build works with Python:

```bash
cd Builds/MacOSX/build/Debug  # or wherever librenderman.so is located
python3
>>> import librenderman as rm
>>> # If no errors, the build was successful!
```

## Troubleshooting

### If you get boost_python312 not found:
- Check what boost python libraries are available: `ls /opt/homebrew/lib/libboost_python*`
- Update the library name in the XCode project to match your installed version
- Or create a symlink as shown above

### If you get Python header not found:
- Verify Python 3.12 is installed: `python3.12 --version`
- Check header location: `python3.12-config --includes`
- Update header search paths in XCode project if needed

### If build fails with architecture errors:
- Ensure you're building for the correct architecture in Xcode
- Try cleaning the build folder (Product → Clean Build Folder)
- Verify ARCHS setting in build configuration

## Notes for JUCE Project Regeneration

If you need to regenerate the XCode project from the .jucer file using JUCE Projucer:
1. The .jucer files have been updated with modern paths
2. You may need to re-apply some XCode-specific settings manually
3. Ensure the architecture setting remains "arm64,x86_64" for Universal Binary support