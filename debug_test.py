#!/usr/bin/env python3
"""
RenderMan Debug Test Script

This script helps verify that RenderMan is properly built and configured.
It tests basic functionality and provides debugging information.
"""

import os
import sys
import traceback
import platform

def print_system_info():
    """Print system information for debugging"""
    print("=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print()

def test_import():
    """Test basic import"""
    print("=== Testing Import ===")
    try:
        import librenderman as rm
        print("✅ librenderman import successful")
        return rm
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Possible solutions:")
        print("  - Ensure librenderman.so is in current directory or PYTHONPATH")
        print("  - Check that the library was built successfully")
        print("  - Verify Python version compatibility")
        return None

def test_engine_creation(rm):
    """Test engine creation"""
    print("=== Testing Engine Creation ===")
    try:
        engine = rm.RenderEngine(44100, 512, 512)
        print("✅ RenderEngine creation successful")
        print(f"  Sample Rate: 44100 Hz")
        print(f"  Buffer Size: 512 samples")
        print(f"  FFT Size: 512")
        return engine
    except Exception as e:
        print(f"❌ Engine creation failed: {e}")
        traceback.print_exc()
        return None

def test_plugin_discovery(engine, plugin_path):
    """Test plugin discovery"""
    print(f"=== Testing Plugin Discovery ===")
    print(f"Scanning path: {plugin_path}")
    
    if not os.path.exists(plugin_path):
        print(f"⚠️  Plugin path does not exist: {plugin_path}")
        return {}
    
    try:
        plugins = engine.get_available_plugin_names(plugin_path)
        print(f"✅ Found {len(plugins)} plugins")
        
        if plugins:
            print("Available plugins:")
            for name, index in plugins.items():
                print(f"  {index}: {name}")
        else:
            print("⚠️  No plugins found in the specified path")
            print("Common plugin locations:")
            if platform.system() == "Linux":
                print("  - /usr/lib/vst")
                print("  - /usr/local/lib/vst")
                print("  - ~/.vst")
            elif platform.system() == "Darwin":  # macOS
                print("  - /Library/Audio/Plug-Ins/VST")
                print("  - ~/Library/Audio/Plug-Ins/VST")
                print("  - /Library/Audio/Plug-Ins/Components")
            elif platform.system() == "Windows":
                print("  - C:\\Program Files\\VstPlugins")
                print("  - C:\\Program Files\\Common Files\\VST2")
        
        return plugins
    except Exception as e:
        print(f"❌ Plugin discovery failed: {e}")
        traceback.print_exc()
        return {}

def test_basic_functionality(engine, plugins):
    """Test basic engine functionality"""
    print("=== Testing Basic Functionality ===")
    
    try:
        # Test parameter size before loading plugin
        param_size = engine.get_plugin_parameter_size()
        print(f"Parameters before plugin load: {param_size}")
        
        if plugins:
            # Try to load the first plugin
            plugin_name = list(plugins.keys())[0]
            plugin_index = plugins[plugin_name]
            print(f"Attempting to load plugin: {plugin_name} (index {plugin_index})")
            
            # Note: We can't actually load without a valid plugin path
            # This is just testing the parameter interface
        
        # Test patch operations
        empty_patch = engine.get_patch()
        print(f"✅ get_patch() returned {len(empty_patch)} parameters")
        
        # Test setting an empty patch
        engine.set_patch([])
        print("✅ set_patch() with empty patch successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug test function"""
    print("RenderMan Debug Test Script")
    print("=" * 50)
    print()
    
    print_system_info()
    
    # Test import
    rm = test_import()
    if not rm:
        print("\n❌ Cannot proceed without successful import")
        return 1
    
    # Test engine creation  
    engine = test_engine_creation(rm)
    if not engine:
        print("\n❌ Cannot proceed without successful engine creation")
        return 1
    
    # Determine plugin path
    if len(sys.argv) > 1:
        plugin_path = sys.argv[1]
    else:
        # Use default paths based on platform
        if platform.system() == "Linux":
            plugin_path = "/usr/lib/vst"
        elif platform.system() == "Darwin":
            plugin_path = "/Library/Audio/Plug-Ins/VST"
        elif platform.system() == "Windows":
            plugin_path = "C:\\Program Files\\VstPlugins"
        else:
            plugin_path = "."
    
    # Test plugin discovery
    plugins = test_plugin_discovery(engine, plugin_path)
    
    # Test basic functionality
    success = test_basic_functionality(engine, plugins)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Debug test completed successfully!")
        print("RenderMan appears to be working correctly.")
        if not plugins:
            print("⚠️  Consider installing VST plugins for full functionality testing")
    else:
        print("❌ Debug test encountered errors")
        print("See error messages above for troubleshooting guidance")
        return 1
    
    print(f"\nFor more debugging information, see render-man-debug.md")
    return 0

if __name__ == "__main__":
    sys.exit(main())