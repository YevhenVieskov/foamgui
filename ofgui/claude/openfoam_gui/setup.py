"""Setup script for OpenFOAM GUI"""
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='openfoam-gui',
    version='1.0.0',
    description='Star-CCM+ like GUI for OpenFOAM 2506',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OpenFOAM GUI Team',
    python_requires='>=3.8',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt6>=6.5.0',
        'pyvista>=0.42.0',
        'pyvistaqt>=0.11.0',
        'vtk>=9.2.0',
        'numpy>=1.24.0',
        'scipy>=1.10.0',
        'matplotlib>=3.7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-qt>=4.2.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'openfoam-gui=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
