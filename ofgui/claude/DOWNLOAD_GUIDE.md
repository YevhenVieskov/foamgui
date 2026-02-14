# 📥 OpenFOAM GUI - Download & Installation Guide

**Version:** 1.0.0  
**Release Date:** February 13, 2026  
**License:** MIT

---

## 📦 Available Downloads

### Archives

| File | Size | Format | Platform | Checksum |
|------|------|--------|----------|----------|
| **openfoam_gui.tar.gz** | 102 KB | tar.gz | Linux/macOS | See CHECKSUMS.md5 |
| **openfoam_gui.zip** | 143 KB | zip | Windows/Universal | See CHECKSUMS.sha256 |
| **openfoam_gui/** | 414 KB | Directory | All | - |

### Supporting Files

- **ARCHIVE_INFO.txt** - Complete archive information
- **RELEASE_NOTES.md** - Release notes and changelog
- **CHECKSUMS.md5** - MD5 checksums for verification
- **CHECKSUMS.sha256** - SHA256 checksums for verification

---

## ✅ Verification

### Verify Archive Integrity

**MD5:**
```bash
md5sum -c CHECKSUMS.md5
```

**SHA256:**
```bash
sha256sum -c CHECKSUMS.sha256
```

### Expected Checksums

**MD5:**
```
e0f5de0997cac8518607f87b2f8b1d0b  openfoam_gui.tar.gz
95ee9eb308ec4f95aaf4fb8948e5dd0a  openfoam_gui.zip
```

**SHA256:**
```
d80112c5de75101b500663432553d3725cde69da4492ce6404dd5f6ac23014bc  openfoam_gui.tar.gz
ac35996e398320dd03579d8a71766d1ed29c70c27cd2277e6eb98649e9d56029  openfoam_gui.zip
```

---

## 🚀 Quick Start

### Linux/macOS

```bash
# Download and extract
tar -xzf openfoam_gui.tar.gz
cd openfoam_gui

# Install
bash install.sh

# Run
openfoam-gui
```

### Windows (WSL2)

```bash
# Extract
unzip openfoam_gui.zip
cd openfoam_gui

# Install
bash install.sh

# Run
python main.py
```

---

## 📋 Installation Options

### 1. Universal Installer (Recommended)

**One command install:**
```bash
cd openfoam_gui
bash install.sh
```

**Features:**
- ✅ Auto-detects OS (Ubuntu, Debian, Fedora, macOS, WSL)
- ✅ Installs system dependencies
- ✅ Creates virtual environment
- ✅ Installs Python packages
- ✅ Creates launcher script
- ✅ Adds to PATH
- ✅ Verifies installation

### 2. Docker (Containerized)

**Build and run:**
```bash
cd openfoam_gui
docker-compose up -d
```

**Features:**
- ✅ Isolated environment
- ✅ Pre-installed OpenFOAM
- ✅ X11 GUI support
- ✅ Volume mounts
- ✅ Easy cleanup

### 3. Manual Installation

**For developers:**
```bash
cd openfoam_gui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## 📖 Documentation

### Getting Started

1. **ARCHIVE_INFO.txt** - What's in the archive
2. **README.md** - Main user guide
3. **QUICK_START.md** - Quick reference
4. **INSTALL.md** - Detailed installation

### Technical Documentation

- **docs/COMPONENT_GUIDE.md** - How components work (2,700 lines)
- **docs/DEVELOPER_GUIDE.md** - Development guide
- **docs/API.md** - API reference
- **ENHANCEMENTS.md** - New features detailed

### Examples

- **examples/cavity/** - Working lid-driven cavity case
- **examples/README.md** - Example cases guide

---

## 🔧 System Requirements

### Minimum Requirements

- **OS:** Linux, macOS 11+, Windows 10/11 (WSL2)
- **Python:** 3.8 or higher
- **RAM:** 4GB
- **Disk:** 2GB (with dependencies)
- **GPU:** OpenGL 3.0+ capable

### Recommended

- **RAM:** 8GB or more
- **CPU:** Multi-core processor
- **GPU:** Dedicated graphics card
- **Disk:** SSD for better performance

### Dependencies

**Core:**
- PyQt6 >= 6.5.0
- pyvista >= 0.42.0
- vtk >= 9.2.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0

**OpenFOAM:**
- OpenFOAM 2506 or compatible version

---

## 🎯 What's Included

### Source Code (32 Python files)
- Core functionality
- UI widgets
- Solver definitions (40+ solvers)
- Mesh quality checking
- Utilities

### Tests (101+ test cases)
- Unit tests (17+)
- GUI automation tests (29)
- Performance tests (18)
- Integration tests

### Documentation (10,000+ lines)
- User guides
- Technical documentation
- API reference
- Examples and tutorials

### Deployment
- Universal installer script
- Dockerfile
- Docker Compose
- Makefile

---

## ⚡ First Steps After Installation

### 1. Verify Installation

```bash
# Check dependencies
python -c "import PyQt6; import pyvista; print('OK')"

# Run tests
cd openfoam_gui
./run_tests.sh
```

### 2. Launch Application

```bash
openfoam-gui
# or
python main.py
```

### 3. Try Example Case

```bash
cd examples/cavity
python create_case.py
cd cavity
blockMesh
icoFoam
```

### 4. Explore Documentation

```bash
# Read main docs
cat README.md
cat QUICK_START.md

# Deep dive
cat docs/COMPONENT_GUIDE.md
```

---

## 🐛 Troubleshooting

### Installation Issues

**Problem:** Dependencies fail to install  
**Solution:** Check Python version (3.8+), update pip

**Problem:** X11 errors in Docker  
**Solution:** Run `xhost +local:docker` before starting

**Problem:** OpenFOAM not found  
**Solution:** Set `openfoam_path` in config.json

### Runtime Issues

**Problem:** GUI doesn't start  
**Solution:** Check PyQt6 installation, verify display

**Problem:** Tests fail  
**Solution:** Install test dependencies: `pip install pytest pytest-qt`

**Problem:** Slow performance  
**Solution:** Check system resources, close other applications

---

## 📊 Project Statistics

- **Files:** 66 total
- **Code:** ~15,000 lines
- **Documentation:** 10,000+ lines
- **Tests:** 101+ automated tests
- **Solvers:** 40+ supported
- **Archive Size:** 102 KB (tar.gz)

---

## 🤝 Getting Help

### Documentation
- See `docs/` directory for technical documentation
- Read `INSTALL.md` for installation help
- Check `examples/` for working cases

### Community
- GitHub Issues (when published)
- GitHub Discussions (when published)
- Project website (when available)

---

## 📄 License

MIT License - Free and open source

See LICENSE file in archive for full text.

---

## 🎉 What's Next?

After installation:

1. ✅ **Launch the GUI** - `openfoam-gui`
2. ✅ **Create a case** - File → New Case
3. ✅ **Generate mesh** - Mesh → blockMesh Editor
4. ✅ **Run simulation** - Solver → Run Solver
5. ✅ **Monitor results** - Real-time visualization

Enjoy using OpenFOAM GUI! 🚀

---

**Questions?** See documentation in the archive.  
**Issues?** Check troubleshooting section above.  
**Feedback?** We'd love to hear from you!

