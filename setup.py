import os.path as osp
import warnings

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


def readme():
    with open('README.md') as f:
        content = f.read()
    return content


def numpy_include():
    import numpy as np
    try:
        numpy_include = np.get_include()
    except AttributeError:
        numpy_include = np.get_numpy_include()
    return numpy_include


def get_ext_modules():
    """The Cython rank evaluator, when Cython and numpy are importable at build time.

    `prtreid.metrics.rank` falls back to the pure-Python evaluation when the extension is
    missing, so it is an accelerator, not a requirement.
    """
    try:
        from Cython.Build import cythonize
        ext_modules = [
            Extension(
                'prtreid.metrics.rank_cylib.rank_cy',
                ['prtreid/metrics/rank_cylib/rank_cy.pyx'],
                include_dirs=[numpy_include()],
            )
        ]
        return cythonize(ext_modules)
    except ImportError as exc:
        warnings.warn('building prtreid without the Cython rank evaluator: %s' % exc)
        return []


class OptionalBuildExt(build_ext):
    """Build the extension if a C compiler is available; install without it otherwise.

    On Windows the build needs MSVC, which is what previously made prtreid impossible to
    pip install on a machine without Visual Studio.
    """

    def run(self):
        try:
            super().run()
        except Exception as exc:
            warnings.warn('skipping the Cython rank evaluator (no working compiler?): %s' % exc)

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as exc:
            warnings.warn('skipping extension %s: %s' % (ext.name, exc))


def get_requirements(filename='requirements.txt'):
    here = osp.dirname(osp.realpath(__file__))
    with open(osp.join(here, filename), 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    return [line for line in lines if line and not line.startswith('#')]

setup(
    description='A library for deep learning person re-ID in PyTorch',
    license='MIT',
    long_description=readme(),
    packages=find_packages(),
    install_requires=get_requirements(),
    extras_require={"labels": get_requirements("requirements_labels.txt")},
    keywords=['Person Re-Identification', 'Deep Learning', 'Computer Vision'],
    ext_modules=get_ext_modules(),
    cmdclass={'build_ext': OptionalBuildExt},
)
