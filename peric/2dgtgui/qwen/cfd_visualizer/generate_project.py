import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = "caffa_visualizer"

# File contents dictionary
FILES = {
    "requirements.txt": """pyvista>=0.40.0
pyvistaqt>=0.11.0
qtpy>=2.4.0
PyQt5>=5.15.0
numpy>=1.24.0
matplotlib>=3.7.0
pandas>=2.0.0
pytest>=7.4.0
pytest-qt>=4.2.0
vtk>=9.2.0
""",

    "README.md": """# CAFFA Visualizer - Star CCM+ Style

A Star CCM+ like CFD visualization tool for CAFFA simulation results built with Python, PyVista, and PyQt.

## Features
- **Star CCM+ Style Interface**: Simulation tree, dockable panels, toolbar
- **3D Visualization**: Vector fields, pressure/velocity contours, plane sections, streamlines
- **Residual Monitoring**: Star CCM+ style convergence plots with log scale
- **CAFFA Support**: Parse .out, .re, .grd files from CAFFA CFD solver
- **Export Capabilities**: Save scenes, export data to CSV

## Installation
```bash
pip install -r requirements.txt