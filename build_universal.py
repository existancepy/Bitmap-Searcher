#!/usr/bin/env python3
"""
Script to build for multiple architectures and Python versions.
Automatically detects the Python version being used to run this script.
"""
import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path

def get_current_python_version():
    """Get the current Python version (e.g., '3.9', '3.8')."""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def get_current_python_executable():
    """Get the current Python executable path."""
    return sys.executable

def build_for_python_version(python_exe, version, arch=None):
    """Build for specific Python version and architecture."""
    print(f"Building for Python {version} using {python_exe}")
    
    env = os.environ.copy()
    
    # Set architecture-specific flags for macOS
    if arch and platform.system() == 'Darwin':
        if arch == 'arm64':
            env['ARCHFLAGS'] = '-arch arm64'
            env['_PYTHON_HOST_PLATFORM'] = 'macosx-11.0-arm64'
        elif arch == 'x86_64':
            env['ARCHFLAGS'] = '-arch x86_64'
            env['_PYTHON_HOST_PLATFORM'] = 'macosx-10.9-x86_64'
    
    build_dir = f'build_py{version.replace(".", "")}'
    if arch:
        build_dir += f'_{arch}'
    
    cmd = [
        python_exe, 'setup_universal.py', 
        'build_ext', '--inplace',
        '--build-temp', build_dir
    ]
    
    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"Successfully built for Python {version}" + (f" ({arch})" if arch else ""))
        
        #copy built extension to dist
        output_dir = Path('dist')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        #only copy extensions that match the current Python version
        version_tag = f"cpython-{version.replace('.', '')}"
        matching_extensions = []
        
        for ext_file in Path('.').glob('bitmap_matcher*.so'):
            if version_tag in ext_file.name:
                matching_extensions.append(ext_file)
        
        if not matching_extensions:
            print(f"Warning: No extensions found for Python {version}")
            return False
        
        for ext_file in matching_extensions:
            if arch:
                dest_name = f'bitmap_matcher_py{version.replace(".", "")}_{arch}.so'
            else:
                dest_name = f'bitmap_matcher_py{version.replace(".", "")}.so'
            
            dest_path = output_dir / dest_name
            shutil.copy2(ext_file, dest_path)
            print(f"Copied {ext_file} to {dest_path}")
            
            #verify the extension can be loaded
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("test_module", dest_path)
                if spec and spec.loader:
                    print(f"Extension {dest_name} appears to be loadable")
                else:
                    print(f"Extension {dest_name} may have issues")
            except Exception as e:
                print(f"Could not verify extension {dest_name}: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build for Python {version}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_dependencies(python_exe):
    #check if required dependencies are installed for given Python.
    required_packages = ['setuptools', 'cython', 'numpy']
    
    for package in required_packages:
        try:
            subprocess.run(
                [python_exe, '-c', f'import {package}'], 
                check=True, 
                capture_output=True
            )
        except subprocess.CalledProcessError:
            print(f"Warning: {package} not found for {python_exe}")
            print(f"Install with: {python_exe} -m pip install {package}")
            return False
    
    return True

def build_for_current_python():
    #build for the current Python version only
    current_version = get_current_python_version()
    current_python = get_current_python_executable()
    current_arch = platform.machine()
    
    print(f"Detected Python {current_version} at: {current_python}")
    print(f"Current architecture: {current_arch}")
    print("-" * 50)
    
    successful_builds = []
    failed_builds = []
    
    #clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    
    #check dependencies
    if not check_dependencies(current_python):
        print(f"✗ Missing dependencies for Python {current_version}")
        print("Install dependencies with: python -m pip install setuptools cython numpy")
        return
    
    #build for current architecture
    if build_for_python_version(current_python, current_version, current_arch):
        successful_builds.append(f"Python {current_version} ({current_arch})")
    else:
        failed_builds.append(f"Python {current_version} ({current_arch})")
    
    #on macOS, try to build for other architecture too
    if platform.system() == 'Darwin':
        other_arch = 'x86_64' if current_arch == 'arm64' else 'arm64'
        print(f"Attempting cross-compilation for {other_arch}...")
        
        if build_for_python_version(current_python, current_version, other_arch):
            successful_builds.append(f"Python {current_version} ({other_arch})")
        else:
            print(f"Cross-compilation for {other_arch} failed (this is normal)")
    
    print()
    
    # Summary
    print("=" * 50)
    print("BUILD SUMMARY")
    print("=" * 50)
    
    if successful_builds:
        print("Successful builds:")
        for build in successful_builds:
            print(f"  {build}")
    
    if failed_builds:
        print("\nFailed builds:")
        for build in failed_builds:
            print(f"  {build}")
    
    print(f"\nTotal: {len(successful_builds)} successful, {len(failed_builds)} failed")

def install_dependencies():
    """Install dependencies for current Python version."""
    current_python = get_current_python_executable()
    current_version = get_current_python_version()
    
    print(f"Installing dependencies for Python {current_version}...")
    
    try:
        subprocess.run([
            current_python, '-m', 'pip', 'install', 
            'setuptools', 'cython', 'numpy'
        ], check=True)
        print(f"Dependencies installed for Python {current_version}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies for Python {current_version}: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build bitmap_matcher for the current Python version',
        epilog='Example usage:\n'
               '  python3.9 build_script.py          # Build for Python 3.9\n'
               '  python3.11 build_script.py         # Build for Python 3.11\n'
               '  python3.8 build_script.py --install-deps  # Install deps for Python 3.8',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install dependencies for current Python version')
    parser.add_argument('--show-info', action='store_true',
                       help='Show current Python version and exit')
    
    args = parser.parse_args()
    
    if args.show_info:
        current_version = get_current_python_version()
        current_python = get_current_python_executable()
        print(f"Current Python version: {current_version}")
        print(f"Current Python executable: {current_python}")
        print(f"Current architecture: {platform.machine()}")
        print(f"Current platform: {platform.system()}")
    elif args.install_deps:
        install_dependencies()
    else:
        build_for_current_python()