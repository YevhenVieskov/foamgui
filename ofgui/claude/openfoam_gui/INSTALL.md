# Installation Guide

## System Requirements

### Operating System
- Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+, or similar)
- macOS 11.0+ (Big Sur or later)
- Windows 10/11 with WSL2

### Software Requirements
- Python 3.8 or higher
- OpenFOAM 2506 or compatible version
- OpenGL 3.0+ capable graphics card
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Update package manager
sudo apt update  # Ubuntu/Debian
# sudo dnf update  # Fedora

# Install system dependencies
sudo apt install python3-pip python3-venv libgl1-mesa-dev

# Clone repository
git clone https://github.com/yourusername/openfoam-gui.git
cd openfoam-gui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Run application
openfoam-gui
```

### Method 2: Development Install

```bash
# Clone repository
git clone https://github.com/yourusername/openfoam-gui.git
cd openfoam-gui

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-qt pytest-cov black flake8 mypy

# Run from source
python main.py
```

### Method 3: Docker (Experimental)

```bash
# Build Docker image
docker build -t openfoam-gui .

# Run container
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/openfoam-cases:/cases \
    openfoam-gui
```

## OpenFOAM Installation

### Ubuntu/Debian

```bash
# Add OpenFOAM repository
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key | apt-key add -"
sudo add-apt-repository http://dl.openfoam.org/ubuntu

# Install OpenFOAM
sudo apt-get update
sudo apt-get install openfoam2506

# Source OpenFOAM environment
echo "source /opt/openfoam2506/etc/bashrc" >> ~/.bashrc
source ~/.bashrc
```

### From Source

```bash
# Download OpenFOAM
wget https://github.com/OpenFOAM/OpenFOAM-v2506/archive/refs/tags/v2506.tar.gz
tar -xzf v2506.tar.gz
cd OpenFOAM-v2506

# Compile (this takes time)
./Allwmake -j
```

## Verification

### Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
./run_tests.sh

# Launch GUI
python main.py
```

### Check OpenFOAM

```bash
# Verify OpenFOAM is accessible
which blockMesh
which simpleFoam

# Should output paths like:
# /opt/openfoam2506/bin/blockMesh
# /opt/openfoam2506/bin/simpleFoam
```

## Troubleshooting

### PyQt6 Installation Issues

```bash
# Install Qt dependencies
sudo apt install qt6-base-dev qt6-tools-dev

# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

### PyVista Display Issues

```bash
# Install Mesa libraries
sudo apt install libgl1-mesa-glx libgl1-mesa-dev

# For headless servers
export PYVISTA_OFF_SCREEN=true
```

### Permission Errors

```bash
# Fix pip permissions
pip install --user -e .

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

### First Run

On first run, the application will create:
- Configuration directory: `~/.openfoam_gui/`
- Configuration file: `~/.openfoam_gui/config.json`

### OpenFOAM Path Configuration

Edit `~/.openfoam_gui/config.json`:

```json
{
  "openfoam_path": "/opt/openfoam2506",
  ...
}
```

Or set via GUI:
1. **File → Preferences**
2. Set OpenFOAM installation path
3. Click Save

## Uninstallation

```bash
# Remove package
pip uninstall openfoam-gui

# Remove configuration (optional)
rm -rf ~/.openfoam_gui

# Remove virtual environment
deactivate
rm -rf venv
```

## Getting Help

- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/yourusername/openfoam-gui/issues
- **Email**: support@example.com
