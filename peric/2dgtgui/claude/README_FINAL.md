# CAFFA CFD Visualization GUI

A Star CCM+ style graphical user interface for visualizing CAFFA (Computer Aided Fluid Flow Analysis) CFD results. Built with PyQt5, PyVista, and VTK for professional-grade 3D visualization.

## 📋 Overview

This package provides a complete visualization solution for CAFFA CFD solver results with:

- **Professional 3D Visualization** - PyVista/VTK-based interactive rendering
- **Star CCM+ Style Interface** - Familiar workflow for CFD engineers  
- **Multiple Visualization Modes** - Contours, vectors, streamlines, mesh overlay
- **Alternative Viewers** - Matplotlib-based viewer for systems without VTK
- **Comprehensive Testing** - 30+ unit and functional tests
- **Production Ready** - Clean code, full documentation

## ✨ Features

### Visualization Capabilities

✅ Scalar field contours (pressure, temperature, velocity)  
✅ Vector field display with adjustable scaling  
✅ Streamline generation and visualization  
✅ Computational mesh grid overlay  
✅ Multi-level contour plots with customizable colormaps  
✅ Interactive 3D manipulation (zoom, pan, rotate)  
✅ Real-time field statistics and data analysis  
✅ Export to PNG, PDF, SVG formats  

### Supported CAFFA Data

- Binary output files (.pos format)
- Structured 2D body-fitted grids
- Transient and steady-state results
- Velocity fields (U, V, magnitude)
- Pressure, Temperature
- Turbulence (k-ω model: TKE, dissipation)

## 🚀 Quick Start

### Option 1: PyQt/PyVista GUI (Recommended)

```bash
# Install dependencies
pip install PyQt5 pyvista vtk numpy matplotlib

# Launch the GUI
python caffa_gui.py

# Load sample data from File menu
# Or open your own .pos file
```

### Option 2: Matplotlib Viewer (Lightweight)

```bash
# Minimal dependencies
pip install numpy matplotlib

# Launch the viewer
python caffa_viewer_matplotlib.py
```

## 📦 Installation

### Full Installation

```bash
# Create virtual environment (recommended)
python -m venv caffa_env
source caffa_env/bin/activate  # On Windows: caffa_env\Scripts\activate

# Install all dependencies
pip install PyQt5 pyvista vtk numpy scipy matplotlib

# Optional: Testing framework
pip install pytest pytest-qt
```

### System Requirements

- Python 3.7+
- 4GB RAM minimum (8GB recommended for large datasets)
- Graphics card with OpenGL 3.2+ support (for PyVista)

## 📚 Usage Guide

### Loading Data

**From GUI:**
1. Launch application: `python caffa_gui.py`
2. File → Open Result File... or Load Sample Data
3. Select field from dropdown menu
4. Enable visualization options (contours, vectors, etc.)

**Programmatically:**

```python
from caffa_reader import CAFFAReader

# Load CAFFA binary file
reader = CAFFAReader()
data = reader.read_binary_file('cavity.pos')

# Access grid information
print(f"Grid: {data.grid.ni} x {data.grid.nj}")
print(f"Time: {data.time}")

# Extract fields
x, y = reader.get_coordinates()
velocity = reader.get_cell_centered_data('vmag')
pressure = reader.get_cell_centered_data('p')
```

### Visualization Examples

**Contour Plot:**

```python
import matplotlib.pyplot as plt

# Get data
x, y = reader.get_coordinates()
temp = reader.get_cell_centered_data('t')

# Plot
plt.contourf(x, y, temp, levels=20, cmap='hot')
plt.colorbar(label='Temperature')
plt.axis('equal')
plt.show()
```

**Vector Field:**

```python
u = reader.get_cell_centered_data('u')
v = reader.get_cell_centered_data('v')

step = 5  # Subsample for clarity
plt.quiver(x[::step, ::step], y[::step, ::step],
           u[::step, ::step], v[::step, ::step])
plt.show()
```

**Streamlines:**

```python
plt.streamplot(x, y, u, v, density=2, color='k')
plt.show()
```

## 🧪 Testing

### Run Tests

```bash
# Unit tests (19 tests)
python test_caffa_reader.py

# Functional tests (11 tests)
python test_functional.py

# All tests with pytest
pytest test_*.py -v
```

### Test Coverage

✓ Data structure validation  
✓ File I/O operations  
✓ Binary format reading  
✓ Field calculations  
✓ Coordinate transformations  
✓ Visualization workflows  
✓ Error handling  
✓ Performance tests  

**Total: 30 tests - All passing ✓**

## 📁 File Structure

```
caffa-gui/
│
├── caffa_reader.py              # Core data reading module
│   ├── CAFFAGrid class         # Grid geometry
│   ├── CAFFAData class         # Solution data
│   └── CAFFAReader class       # File I/O
│
├── caffa_gui.py                 # PyQt5/PyVista GUI
│   ├── Menu system
│   ├── 3D visualization
│   ├── Control panels
│   └── Statistics display
│
├── caffa_viewer_matplotlib.py   # Matplotlib alternative
│   ├── Tkinter GUI
│   ├── 2D plotting
│   └── Export capabilities
│
├── test_caffa_reader.py         # Unit tests
│   └── 19 test cases
│
├── test_functional.py           # Functional tests  
│   └── 11 workflow tests
│
└── README.md                    # This file
```

## 🔧 API Reference

### CAFFAReader Class

```python
class CAFFAReader:
    def read_binary_file(filename: str) -> CAFFAData
        """Read CAFFA binary output file"""
    
    def get_coordinates() -> Tuple[np.ndarray, np.ndarray]
        """Get grid coordinates as 2D arrays"""
    
    def get_cell_centered_data(field_name: str) -> np.ndarray
        """Extract field data reshaped to grid"""
```

**Supported field names:**
- `'u'`, `'v'` - Velocity components
- `'p'` - Pressure  
- `'t'`, `'temperature'` - Temperature
- `'te'`, `'tke'` - Turbulent kinetic energy
- `'dissipation'` - Dissipation rate
- `'vmag'`, `'velocity_magnitude'` - Velocity magnitude

### CAFFAData Class

```python
@dataclass
class CAFFAData:
    itim: int                    # Time step number
    time: float                  # Physical time
    grid: CAFFAGrid             # Grid information
    u, v: np.ndarray            # Velocity components
    p: np.ndarray               # Pressure
    t: np.ndarray               # Temperature
    te: np.ndarray              # Turbulent kinetic energy
    dissipation: np.ndarray     # Dissipation rate
    
    @property
    def velocity_magnitude(self) -> np.ndarray
        """Computed velocity magnitude"""
```

## 🎨 GUI Features

### Main Window Layout

```
┌─────────────────────────────────────────────────────┐
│  File  View  Tools  Help                            │
├──────────┬──────────────────────────┬───────────────┤
│ Controls │  3D Visualization        │  Information  │
│          │                          │               │
│ Field    │      PyVista/VTK         │  Dataset Info │
│ Select   │      Interactive         │               │
│          │      Viewport            │  Statistics   │
│ Vis      │                          │               │
│ Options  │                          │  Min/Max      │
│          │                          │  Mean/StdDev  │
│ Settings │                          │               │
└──────────┴──────────────────────────┴───────────────┘
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file |
| Ctrl+S | Export screenshot |
| Ctrl+Q | Quit |
| R | Reset camera view |

## 📊 CAFFA File Format

The reader supports CAFFA Fortran unformatted binary files:

```fortran
! Post-processing file format
WRITE(8) ITIM,TIME,NI,NJ,NIM,NJM,NIJ,
         (X(IJ), IJ=IJST,IJEN),    ! Grid X coordinates
         (Y(IJ), IJ=IJST,IJEN),    ! Grid Y coordinates
         (XC(IJ),IJ=IJST,IJEN),    ! Cell center X
         (YC(IJ),IJ=IJST,IJEN),    ! Cell center Y
         (F1(IJ),IJ=IJST,IJEN),    ! Mass flux I-direction
         (F2(IJ),IJ=IJST,IJEN),    ! Mass flux J-direction
         (U(IJ), IJ=IJST,IJEN),    ! U velocity
         (V(IJ), IJ=IJST,IJEN),    ! V velocity
         (P(IJ), IJ=IJST,IJEN),    ! Pressure
         (T(IJ), IJ=IJST,IJEN),    ! Temperature
         (TE(IJ),IJ=IJST,IJEN),    ! Turb. kinetic energy
         (AP(IJ),IJ=IJST,IJEN)     ! Dissipation
```

## 🐛 Troubleshooting

### "PyQt5 not found"
```bash
pip install PyQt5
# Or use matplotlib viewer: python caffa_viewer_matplotlib.py
```

### "VTK import error"
```bash
pip install vtk pyvista
# Or use matplotlib viewer for 2D visualization
```

### "Binary file reading error"
- Ensure file is CAFFA format (.pos)
- Check Fortran record markers are correct
- Verify grid dimensions match file size

### Slow visualization
- Reduce grid resolution  
- Disable vectors/streamlines for large datasets
- Use contours only mode

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] 3D grid support
- [ ] Animation for transient results
- [ ] Additional post-processing tools
- [ ] Batch processing mode
- [ ] Grid file (.grd) reader
- [ ] Export to VTK format

## 📄 License

This visualization tool is provided for use with CAFFA CFD solver.

CAFFA original code:
> M. Peric, Hamburg, 1996  
> M. Schmid, Hamburg, 1997  
> CAFFA - Computer Aided Fluid Flow Analysis

## 🙏 Credits

- GUI design inspired by Star CCM+
- Built with PyQt5, PyVista, VTK, Matplotlib
- CAFFA solver by M. Peric and M. Schmid

## 📧 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the test files for usage examples

## 📌 Version

**v1.0** - February 2026
- Initial release
- PyQt5/PyVista 3D GUI
- Matplotlib 2D viewer
- Binary file reader
- 30 comprehensive tests
- Full documentation

---

**Made for CFD engineers by CFD engineers** 🚀
