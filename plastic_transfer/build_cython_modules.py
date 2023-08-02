from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='EMPP Cython helpers',
    ext_modules=cythonize("cython_helpers.pyx"),
    include_dirs=[numpy.get_include()],
    zip_safe=False,
)

