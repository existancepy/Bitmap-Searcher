# Bitmap Searcher
A fast bitmap seacher written in python and cython for pillow images
This package was designed for my [Bee Swarm Macro](https://github.com/existancepy/bss-macro-py)  

Note: You are expected to build the binaries

# Build instructions
Supported python versions: 3.7 and above<br>
Supported OS: Windows, Mac, Linux

### Download the source code
Download the source code from the repo, or with the git module

### Install dependencies
```console
python build_universal.py --install-deps
```

### Build package
```console
python build_universal.py
```

After the build is complete, you can find all the binaries in the /dist folder

# Adding the binary to Existance Macro (Optional)
For users building this binary for the macro  
Place the binary in the macro folder -> src -> modules -> bitmap_matcher

# Usage
You can visit example.py for examples and basic documentation
