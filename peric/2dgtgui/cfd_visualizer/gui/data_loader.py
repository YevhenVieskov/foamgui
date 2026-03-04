"""
CFD Data Loader for CAFFA simulations
"""

from qtpy.QtCore import QObject, Signal, Slot
import numpy as np
import pyvista as pv
from pathlib import Path
from .caffa_parser import CAFFAParser

class CFDDataLoader(QObject):
    """Load CAFFA CFD simulation data"""
    
    data_loaded = Signal(dict)
    error_occurred = Signal(str)
    progress_updated = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.parser = CAFFAParser()
        self.supported_formats = ['.out', '.re', '.grd', '.cin']
    
    @Slot(str)
    def load(self, filepath: str) -> dict:
        """Load CAFFA simulation data"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            ext = filepath.suffix.lower()
            
            if ext == '.out':
                data = self._load_output_file(filepath)
            elif ext == '.re':
                data = self._load_result_file(filepath)
            elif ext == '.grd':
                data = self._load_grid_file(filepath)
            else:
                raise ValueError(f"Unsupported format: {ext}")
            
            data['filepath'] = str(filepath)
            data['filename'] = filepath.name
            
            self.data_loaded.emit(data)
            return data
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            raise
    
    def _load_output_file(self, filepath: Path) -> dict:
        """Load CAFFA output file with residuals"""
        self.progress_updated.emit(20)
        
        data = self.parser.parse_output_file(str(filepath))
        self.progress_updated.emit(60)
        
        # Create sample mesh for visualization
        data['mesh'] = self._create_sample_mesh(data)
        self.progress_updated.emit(100)
        
        return data
    
    def _load_result_file(self, filepath: Path) -> dict:
        """Load CAFFA binary result file"""
        self.progress_updated.emit(30)
        
        data = self.parser.parse_result_file(str(filepath))
        self.progress_updated.emit(70)
        
        # Create mesh from fields
        if 'fields' in data and 'grid_info' in data:
            data['mesh'] = self.parser.create_mesh_from_fields(
                data['fields'], 
                data['grid_info']
            )
        
        self.progress_updated.emit(100)
        return data
    
    def _load_grid_file(self, filepath: Path) -> dict:
        """Load CAFFA grid file"""
        self.progress_updated.emit(40)
        
        data = {
            'grid_info': self._parse_grid_file(filepath),
            'mesh': self._create_mesh_from_grid_file(filepath)
        }
        
        self.progress_updated.emit(100)
        return data
    
    def _parse_grid_file(self, filepath: Path) -> dict:
        """Parse CAFFA grid file"""
        grid_info = {
            'ni': 50,
            'nj': 50,
            'levels': 1
        }
        
        try:
            with open(filepath, 'rb') as f:
                # Read binary grid data
                # Simplified implementation
                pass
        except:
            pass
        
        return grid_info
    
    def _create_mesh_from_grid_file(self, filepath: Path) -> pv.UnstructuredGrid:
        """Create PyVista mesh from CAFFA grid file"""
        # Simplified implementation
        return self._create_sample_mesh({})
    
    def _create_sample_mesh(self, data: dict) -> pv.StructuredGrid:
        """Create sample mesh for visualization"""
        import pyvista as pv
        
        # Create airfoil-like structured grid
        ni = 100
        nj = 50
        
        # Create C-grid around airfoil
        x = np.linspace(-1, 2, ni)
        y = np.linspace(-1, 1, nj)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        # Create airfoil shape (NACA 0012 approximation)
        chord = 1.0
        thickness = 0.12
        
        for i in range(ni):
            for j in range(nj):
                xc = X[i, j]
                if 0 <= xc <= chord:
                    # Airfoil thickness distribution
                    yt = 5 * thickness * (0.2969 * np.sqrt(xc/chord) 
                                         - 0.1260 * (xc/chord)
                                         - 0.3516 * (xc/chord)**2
                                         + 0.2843 * (xc/chord)**3
                                         - 0.1015 * (xc/chord)**4)
                    
                    # Push grid points away from airfoil surface
                    dist = abs(Y[i, j])
                    if dist < 0.2:
                        Y[i, j] = np.sign(Y[i, j]) * (yt + dist * 0.5)
        
        grid = pv.StructuredGrid(X, Y, Z)
        
        # Add sample field data
        n_points = grid.n_points
        
        # Pressure field (lower on top, higher on bottom)
        pressure = -Y[:ni-1, :nj-1].flatten()  # Simplified
        if len(pressure) < n_points:
            pressure = np.pad(pressure, (0, n_points - len(pressure)), mode='edge')
        grid['Pressure'] = pressure[:n_points]
        
        # Velocity field
        velocity = np.zeros((n_points, 3))
        velocity[:, 0] = 1.0 + 0.1 * np.sin(Y[:n_points] * 2 * np.pi)
        velocity[:, 1] = 0.1 * np.cos(X.flatten()[:n_points] * 2 * np.pi)
        grid['Velocity'] = velocity
        
        # Turbulent energy
        te = np.abs(np.random.randn(n_points) * 0.01)
        grid['Turbulent Energy'] = te
        
        return grid
    
    def generate_sample_residuals(self, n_iterations: int = 100) -> list:
        """Generate sample residual history for testing"""
        residuals = []
        
        for i in range(n_iterations):
            residual = {
                'grid': 1,
                'cycle': 1,
                'iteration': i,
                'u_momentum': 10 ** (-3 - i / 30),
                'v_momentum': 10 ** (-3 - i / 30),
                'mass': 10 ** (-3 - i / 25),
                'energy': 10 ** (-3 - i / 35) if i > 10 else 1e-3,
                'turbulent_energy': 10 ** (-3 - i / 40) if i > 20 else 1e-3,
                'dissipation': 10 ** (-3 - i / 45) if i > 30 else 1e-3
            }
            residuals.append(residual)
        
        return residuals