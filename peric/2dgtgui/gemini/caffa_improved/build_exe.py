import PyInstaller.__main__
import os
import shutil

# --- Configuration ---
MAIN_SCRIPT = 'caffa_pro.py'
EXE_NAME = 'PyCAFFA_Pro'

# --- Clean Previous Builds ---
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists(f'{EXE_NAME}.spec'):
    os.remove(f'{EXE_NAME}.spec')

# --- PyInstaller Arguments ---
args = [
    MAIN_SCRIPT,
    f'--name={EXE_NAME}',
    '--onefile',                   # Pack everything into a single .exe
    '--windowed',                  # GUI mode (hides command prompt)
    '--clean',                     # Clean cache before building
    
    # --- Hidden Imports ---
    # Explicitly import backends and dynamic libraries required by VTK/Matplotlib
    '--hidden-import=pkg_resources.py2_warn',
    '--hidden-import=pyvista',
    '--hidden-import=pyvistaqt',
    '--hidden-import=vtk',
    '--hidden-import=vtkmodules',
    '--hidden-import=vtkmodules.all',
    '--hidden-import=matplotlib',
    '--hidden-import=matplotlib.backends.backend_qt5agg',
    '--hidden-import=PyQt6',
    '--hidden-import=numpy',
    
    # --- Data Collection ---
    # Ensures configuration files for these libs are included
    '--collect-all=pyvista',
    '--collect-all=matplotlib',
    '--collect-all=vtkmodules',
]

print("-------------------------------------------------")
print(f"Starting Build for {MAIN_SCRIPT}...")
print("-------------------------------------------------")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\n-------------------------------------------------")
print(f"Build Finished Successfully.")
print(f"Executable is located at: dist/{EXE_NAME}.exe")
print("-------------------------------------------------")