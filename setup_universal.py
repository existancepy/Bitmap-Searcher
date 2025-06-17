from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import platform
import sys

def get_extensions():
    """Configure extensions for better compatibility."""
    
    extensions = [
        Extension(
            "bitmap_matcher",
            ["bitmap_matcher.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=[
                '-O2',  #less aggressive optimization than -O3
                '-fPIC',  #position independent code
            ],
            extra_link_args=['-O2'],
            define_macros=[
                ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
            ]
        )
    ]
    
    return extensions

setup(
    name="bitmap_matcher",
    ext_modules=cythonize(
        get_extensions(),
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
        }
    ),
    include_dirs=[numpy.get_include()],
    zip_safe=False,
    python_requires='>=3.7,<3.10', #supported Python versions
)