#!/usr/bin/env python3
"""
RenderMan Build Verification Script for M1 Max / macOS Sequoia

This script helps verify that RenderMan is properly built and configured
for your M1 Max system with macOS Sequoia.
"""

import sys
import os
import subprocess
import platform

def check_system_info():
    """Check system information"""
    print("=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"macOS Version: {platform.mac_ver()[0]}")
    print(f"Python Version: {sys.version}")
    print()

def check_python_config():
    """Check Python configuration"""
    print("=== Python Configuration ===")
    try:
        result = subprocess.run(['python3-config', '--includes', '--ldflags'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Python includes and ldflags:")
            print(result.stdout)
        else:
            print("❌ python3-config not found or failed")
    except FileNotFoundError:
        print("❌ python3-config not found")
    print()

def check_homebrew():
    """Check Homebrew installation"""
    print("=== Homebrew Check ===")
    try:
        result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Homebrew installed:")
            print(result.stdout.split('\n')[0])
        else:
            print("❌ Homebrew not working properly")
    except FileNotFoundError:
        print("❌ Homebrew not found")
    print()

def check_boost_python():
    """Check Boost Python installation"""
    print("=== Boost Python Check ===")
    homebrew_lib_path = "/opt/homebrew/lib"
    usr_local_lib_path = "/usr/local/lib"
    
    boost_files = []
    for path in [homebrew_lib_path, usr_local_lib_path]:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.startswith("libboost_python") and file.endswith(".dylib"):
                    boost_files.append(os.path.join(path, file))
    
    if boost_files:
        print("✅ Found Boost Python libraries:")
        for file in boost_files:
            print(f"  {file}")
    else:
        print("❌ No Boost Python libraries found")
        print("   Try: brew install boost-python3")
    print()

def check_xcode():
    """Check Xcode and command line tools"""
    print("=== Xcode Check ===")
    try:
        result = subprocess.run(['xcode-select', '--print-path'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Xcode command line tools path: {result.stdout.strip()}")
        else:
            print("❌ Xcode command line tools not properly configured")
    except FileNotFoundError:
        print("❌ xcode-select not found")
    
    try:
        result = subprocess.run(['xcodebuild', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Xcodebuild version: {result.stdout.split()[1]}")
        else:
            print("❌ xcodebuild not available")
    except FileNotFoundError:
        print("❌ xcodebuild not found")
    print()

def check_renderman_build():
    """Check if RenderMan has been built"""
    print("=== RenderMan Build Check ===")
    build_paths = [
        "Builds/MacOSX/build/Debug/librenderman.so",
        "Builds/MacOSX/build/Release/librenderman.so",
        "Builds/MacOSX/build/Debug/librenderman.so.dylib",
        "Builds/MacOSX/build/Release/librenderman.so.dylib"
    ]
    
    found_builds = []
    for path in build_paths:
        if os.path.exists(path):
            found_builds.append(path)
    
    if found_builds:
        print("✅ Found RenderMan builds:")
        for build in found_builds:
            size = os.path.getsize(build)
            print(f"  {build} ({size:,} bytes)")
    else:
        print("❌ No RenderMan builds found")
        print("   Build the project in Xcode first")
    print()

def test_import():
    """Test importing RenderMan"""
    print("=== Import Test ===")
    
    # Check current directory for librenderman.so
    if os.path.exists("librenderman.so"):
        print("✅ Found librenderman.so in current directory")
        try:
            import librenderman as rm
            print("✅ Successfully imported librenderman!")
            print("🎉 RenderMan is ready to use!")
        except ImportError as e:
            print(f"❌ Failed to import librenderman: {e}")
    else:
        print("❌ librenderman.so not found in current directory")
        print("   Copy it from the build directory or run this script from there")
    print()

def main():
    """Main verification function"""
    print("RenderMan M1 Max / macOS Sequoia Build Verification")
    print("=" * 55)
    print()
    
    check_system_info()
    check_python_config()
    check_homebrew()
    check_boost_python()
    check_xcode()
    check_renderman_build()
    test_import()
    
    print("Verification complete!")
    print("\nFor detailed build instructions, see BUILD_INSTRUCTIONS_M1_SEQUOIA.md")

if __name__ == "__main__":
    main()