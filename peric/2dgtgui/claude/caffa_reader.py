"""
CAFFA Data Reader Module
Reads binary output files from CAFFA CFD solver
"""
import struct
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CAFFAGrid:
    """Stores CAFFA grid information"""
    ni: int  # Number of grid points in I direction
    nj: int  # Number of grid points in J direction
    nim: int  # ni - 1
    njm: int  # nj - 1
    nij: int  # Total number of cells
    x: np.ndarray  # X coordinates
    y: np.ndarray  # Y coordinates
    xc: np.ndarray  # X cell center coordinates
    yc: np.ndarray  # Y cell center coordinates


@dataclass
class CAFFAData:
    """Stores CAFFA solution data"""
    itim: int  # Time step number
    time: float  # Physical time
    grid: CAFFAGrid
    f1: np.ndarray  # Mass flux in I direction
    f2: np.ndarray  # Mass flux in J direction
    u: np.ndarray  # Velocity component U
    v: np.ndarray  # Velocity component V
    p: np.ndarray  # Pressure
    t: np.ndarray  # Temperature
    te: np.ndarray  # Turbulent kinetic energy
    dissipation: np.ndarray  # Turbulent dissipation
    
    @property
    def velocity_magnitude(self) -> np.ndarray:
        """Calculate velocity magnitude"""
        return np.sqrt(self.u**2 + self.v**2)
    
    @property
    def vorticity(self) -> np.ndarray:
        """Calculate vorticity (simplified for structured grid)"""
        # This would need proper gradient calculation for production
        return np.zeros_like(self.u)


class CAFFAReader:
    """Reader for CAFFA binary output files"""
    
    def __init__(self):
        self.data: Optional[CAFFAData] = None
        
    def read_binary_file(self, filename: str) -> CAFFAData:
        """
        Read CAFFA binary output file (.pos file)
        
        Format (Fortran unformatted):
        WRITE(8) ITIM,TIME,NI,NJ,NIM,NJM,NIJ,
                 (X(IJ), IJ=IJST,IJEN),(Y(IJ), IJ=IJST,IJEN),
                 (XC(IJ),IJ=IJST,IJEN),(YC(IJ),IJ=IJST,IJEN),
                 (F1(IJ),IJ=IJST,IJEN),(F2(IJ),IJ=IJST,IJEN),
                 (U(IJ), IJ=IJST,IJEN),(V(IJ), IJ=IJST,IJEN),
                 (P(IJ), IJ=IJST,IJEN),(T(IJ), IJ=IJST,IJEN),
                 (TE(IJ),IJ=IJST,IJEN),(AP(IJ),IJ=IJST,IJEN)
        """
        with open(filename, 'rb') as f:
            # Read Fortran record marker (4 bytes)
            rec_start = struct.unpack('i', f.read(4))[0]
            
            # Read header data
            itim = struct.unpack('i', f.read(4))[0]
            time = struct.unpack('f', f.read(4))[0]
            ni = struct.unpack('i', f.read(4))[0]
            nj = struct.unpack('i', f.read(4))[0]
            nim = struct.unpack('i', f.read(4))[0]
            njm = struct.unpack('i', f.read(4))[0]
            nij = struct.unpack('i', f.read(4))[0]
            
            # Read coordinate arrays
            x = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            y = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            xc = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            yc = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            
            # Read flow field data
            f1 = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            f2 = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            u = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            v = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            p = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            t = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            te = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            dissip = np.array(struct.unpack(f'{nij}f', f.read(4 * nij)))
            
            # Read Fortran record end marker
            rec_end = struct.unpack('i', f.read(4))[0]
            
            # Validate record markers
            if rec_start != rec_end:
                raise ValueError(f"Record marker mismatch: {rec_start} != {rec_end}")
            
            # Create grid object
            grid = CAFFAGrid(ni, nj, nim, njm, nij, x, y, xc, yc)
            
            # Create data object
            self.data = CAFFAData(
                itim, time, grid, f1, f2, u, v, p, t, te, dissip
            )
            
            return self.data
    
    def read_grid_file(self, filename: str) -> CAFFAGrid:
        """Read CAFFA grid file (.grd file)"""
        # Grid file format would need to be implemented based on actual format
        # This is a placeholder
        raise NotImplementedError("Grid file reading not yet implemented")
    
    def get_cell_centered_data(self, field_name: str) -> np.ndarray:
        """Get data at cell centers, reshaped to 2D grid"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        field_map = {
            'u': self.data.u,
            'v': self.data.v,
            'p': self.data.p,
            't': self.data.t,
            'temperature': self.data.t,
            'te': self.data.te,
            'tke': self.data.te,
            'dissipation': self.data.dissipation,
            'velocity_magnitude': self.data.velocity_magnitude,
            'vmag': self.data.velocity_magnitude,
        }
        
        if field_name.lower() not in field_map:
            raise ValueError(f"Unknown field: {field_name}")
        
        field = field_map[field_name.lower()]
        
        # Reshape to 2D grid
        return field.reshape(self.data.grid.nj, self.data.grid.ni)
    
    def get_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get grid coordinates as 2D arrays"""
        if self.data is None:
            raise ValueError("No data loaded")
        
        x = self.data.grid.xc.reshape(self.data.grid.nj, self.data.grid.ni)
        y = self.data.grid.yc.reshape(self.data.grid.nj, self.data.grid.ni)
        
        return x, y


def create_sample_data(ni: int = 50, nj: int = 30) -> CAFFAData:
    """Create sample CAFFA data for testing"""
    nij = ni * nj
    
    # Create grid
    x_1d = np.linspace(0, 1, ni)
    y_1d = np.linspace(0, 1, nj)
    x, y = np.meshgrid(x_1d, y_1d)
    
    x_flat = x.flatten()
    y_flat = y.flatten()
    
    grid = CAFFAGrid(
        ni=ni, nj=nj, nim=ni-1, njm=nj-1, nij=nij,
        x=x_flat, y=y_flat, xc=x_flat, yc=y_flat
    )
    
    # Create sample flow field (driven cavity)
    u = np.sin(np.pi * x) * np.cos(np.pi * y)
    v = -np.cos(np.pi * x) * np.sin(np.pi * y)
    p = -0.25 * (np.cos(2*np.pi*x) + np.cos(2*np.pi*y))
    t = 300 + 50 * np.sin(np.pi * x) * np.sin(np.pi * y)
    te = 0.01 * np.ones_like(x)
    dissip = 0.001 * np.ones_like(x)
    
    return CAFFAData(
        itim=1,
        time=1.0,
        grid=grid,
        f1=np.zeros(nij),
        f2=np.zeros(nij),
        u=u.flatten(),
        v=v.flatten(),
        p=p.flatten(),
        t=t.flatten(),
        te=te.flatten(),
        dissipation=dissip.flatten()
    )
