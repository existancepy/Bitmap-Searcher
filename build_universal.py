#script to build for multiple architectures and Python versions
import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path

#supported python versions
PYTHON_VERSIONS = ['3.7', '3.8', '3.9']

def find_python_executable(version):
    """Find Python executable for given version."""
    possible_names = [
        f'python{version}',
        f'python{version.replace(".", "")}',
        f'py -{version}',  #for windows
    ]
    
    for name in possible_names:
        try:
            #test if this python exists and is correct version
            result = subprocess.run(
                [name, '--version'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            if version in result.stdout:
                return name
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

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
        
        for ext_file in Path('.').glob('bitmap_matcher*.so'):
            if arch:
                dest_name = f'bitmap_matcher_py{version.replace(".", "")}_{arch}.so'
            else:
                dest_name = ext_file.name
            shutil.copy2(ext_file, output_dir / dest_name)
            print(f"Copied {ext_file} to {output_dir / dest_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build for Python {version}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_dependencies(python_exe):
    """Check if required dependencies are installed for given Python."""
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

def build_for_all_versions():
    """Build for all supported Python versions."""
    current_arch = platform.machine()
    print(f"Current architecture: {current_arch}")
    print(f"Target Python versions: {', '.join(PYTHON_VERSIONS)}")
    print("-" * 50)
    
    successful_builds = []
    failed_builds = []
    
    #clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    
    for version in PYTHON_VERSIONS:
        python_exe = find_python_executable(version)
        
        if not python_exe:
            print(f"✗ Python {version} not found")
            failed_builds.append(f"Python {version} (not found)")
            continue
        
        print(f"Found Python {version}: {python_exe}")
        
        #check dependencies
        if not check_dependencies(python_exe):
            failed_builds.append(f"Python {version} (missing dependencies)")
            continue
        
        #build for current architecture
        if build_for_python_version(python_exe, version, current_arch):
            successful_builds.append(f"Python {version} ({current_arch})")
        else:
            failed_builds.append(f"Python {version} ({current_arch})")
        
        #on macOS, try to build for other architecture too
        if platform.system() == 'Darwin':
            other_arch = 'x86_64' if current_arch == 'arm64' else 'arm64'
            print(f"Attempting cross-compilation for {other_arch}...")
            
            if build_for_python_version(python_exe, version, other_arch):
                successful_builds.append(f"Python {version} ({other_arch})")
            else:
                print(f"Cross-compilation for {other_arch} failed (this is normal)")
        
        print()
    
    #summary
    print("=" * 50)
    print("BUILD SUMMARY")
    print("=" * 50)
    
    if successful_builds:
        print("Successful builds:")
        for build in successful_builds:
            print(f"  - {build}")
    
    if failed_builds:
        print("\nFailed builds:")
        for build in failed_builds:
            print(f"  - {build}")
    
    print(f"\nTotal: {len(successful_builds)} successful, {len(failed_builds)} failed")

def install_dependencies():
    """Install dependencies for all Python versions."""
    print("Installing dependencies for all Python versions...")
    
    for version in PYTHON_VERSIONS:
        python_exe = find_python_executable(version)
        if python_exe:
            print(f"Installing for Python {version}...")
            try:
                subprocess.run([
                    python_exe, '-m', 'pip', 'install', 
                    'setuptools', 'cython', 'numpy'
                ], check=True)
                print(f"✓ Dependencies installed for Python {version}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install dependencies for Python {version}: {e}")
        else:
            print(f"Python {version} not found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Build bitmap_matcher for multiple Python versions')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install dependencies for all Python versions')
    parser.add_argument('--python-version', 
                       help='Build for specific Python version only')
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_dependencies()
    elif args.python_version:
        if args.python_version in PYTHON_VERSIONS:
            python_exe = find_python_executable(args.python_version)
            if python_exe and check_dependencies(python_exe):
                build_for_python_version(python_exe, args.python_version, platform.machine())
            else:
                print(f"Python {args.python_version} not available or missing dependencies")
        else:
            print(f"Unsupported Python version: {args.python_version}")
            print(f"Supported versions: {', '.join(PYTHON_VERSIONS)}")
    else:
        build_for_all_versions()