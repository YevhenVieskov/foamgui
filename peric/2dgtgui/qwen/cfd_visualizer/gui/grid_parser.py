"""
CAFFA Grid File Parser
Parses grid.f output files (.grd, .got, .gin)
"""

import numpy as np
import struct
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class GridParser:
    """Parse CAFFA grid generation output files"""
    
    def __init__(self):
        self.grid_levels = 0
        self.boundary_types = {
            1: 'Inlet',
            2: 'Outlet', 
            3: 'Symmetry',
            4: 'Isothermal Wall',
            5: 'Adiabatic Wall',
            10: 'O/C-Grid Cut'
        }
    
    def parse_binary_grid(self, filepath: str) -> Dict:
        """Parse CAFFA binary grid file (.grd)"""
        data = {
            'metadata': {},
            'grid_levels': 0,
            'boundaries': {},
            'coordinates': {},
            'volumes': {},
            'interpolation_factors': {}
        }
        
        try:
            with open(filepath, 'rb') as f:
                # Read header information
                ia = struct.unpack('i', f.read(4))[0]
                data['metadata']['axisymmetric'] = bool(ia)
                
                # Read boundary type arrays
                nxa = self._read_int_array(f, 1)[0]
                data['metadata']['nxa'] = nxa
                
                # Read ITB (I-direction boundary types)
                itb1 = self._read_int_array(f, nxa)
                itb2 = self._read_int_array(f, nxa)
                data['boundaries']['itb_south'] = itb1
                data['boundaries']['itb_north'] = itb2
                
                # Read JTB (J-direction boundary types)
                nya = self._read_int_array(f, 1)[0]
                data['metadata']['nya'] = nya
                
                jtb1 = self._read_int_array(f, nya)
                jtb2 = self._read_int_array(f, nya)
                data['boundaries']['jtb_west'] = jtb1
                data['boundaries']['jtb_east'] = jtb2
                
                # Read grid indexing arrays
                li = self._read_int_array(f, nxa)
                data['grid_indexing'] = {'li': li}
                
                # Read grid level information
                ngr = self._read_int_array(f, 1)[0]
                data['grid_levels'] = ngr
                
                nigr = self._read_int_array(f, ngr)
                njgr = self._read_int_array(f, ngr)
                ijgr = self._read_int_array(f, ngr)
                
                data['grid_info'] = {
                    'nigr': nigr,
                    'njgr': njgr,
                    'ijgr': ijgr
                }
                
                # Read boundary face information
                nina = self._read_int_array(f, 1)[0]
                data['boundaries']['nina'] = nina
                
                # Read coordinate arrays
                nija = self._read_int_array(f, 1)[0]
                data['metadata']['nija'] = nija
                
                x = self._read_float_array(f, nija)
                y = self._read_float_array(f, nija)
                data['coordinates']['x'] = x
                data['coordinates']['y'] = y
                
                # Read cell center coordinates
                xc = self._read_float_array(f, nija)
                yc = self._read_float_array(f, nija)
                data['coordinates']['xc'] = xc
                data['coordinates']['yc'] = yc
                
                # Read interpolation factors
                fx = self._read_float_array(f, nija)
                fy = self._read_float_array(f, nija)
                data['interpolation_factors'] = {'fx': fx, 'fy': fy}
                
                # Read cell volumes
                vol = self._read_float_array(f, nija)
                data['volumes'] = vol
                
                # Read wall boundary data
                nwt = self._read_int_array(f, 1)[0]
                if nwt > 0:
                    srdw = self._read_float_array(f, nwt)
                    xtw = self._read_float_array(f, nwt)
                    ytw = self._read_float_array(f, nwt)
                    data['wall_data'] = {
                        'srdw': srdw,
                        'xtw': xtw,
                        'ytw': ytw
                    }
                
                # Read symmetry boundary data
                nst = self._read_int_array(f, 1)[0]
                if nst > 0:
                    srds = self._read_float_array(f, nst)
                    xns = self._read_float_array(f, nst)
                    yns = self._read_float_array(f, nst)
                    data['symmetry_data'] = {
                        'srds': srds,
                        'xns': xns,
                        'yns': yns
                    }
                
                # Read O/C-grid cut data
                noct = self._read_int_array(f, 1)[0]
                if noct > 0:
                    foc = self._read_float_array(f, noct)
                    data['ocut_data'] = {'foc': foc}
                
        except Exception as e:
            raise IOError(f"Failed to parse CAFFA grid file: {str(e)}")
        
        return data
    
    def parse_text_output(self, filepath: str) -> Dict:
        """Parse CAFFA text output file (.got)"""
        data = {
            'metadata': {},
            'boundary_conditions': {},
            'grid_parameters': {}
        }
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Parse metadata
            for line in lines:
                if 'FLUID DENSITY' in line:
                    data['metadata']['density'] = self._extract_value(line)
                elif 'DYNAMIC VISCOSITY' in line:
                    data['metadata']['viscosity'] = self._extract_value(line)
                elif 'CONVERGENCE CRIT' in line:
                    data['metadata']['convergence_criterion'] = self._extract_value(line)
                elif 'SIP-PARAMETER' in line:
                    data['metadata']['sip_parameter'] = self._extract_value(line)
                elif 'UNDER-RELAXATION' in line:
                    var, value = self._extract_under_relaxation(line)
                    if var:
                        data['metadata'][f'urf_{var}'] = value
                elif 'BLENDING FACTOR' in line:
                    var, value = self._extract_blending_factor(line)
                    if var:
                        data['metadata'][f'gds_{var}'] = value
            
            # Parse boundary conditions
            data['boundary_conditions'] = self._parse_boundary_sections(lines)
            
            # Parse grid parameters
            data['grid_parameters'] = self._parse_grid_parameters(lines)
            
        except Exception as e:
            raise IOError(f"Failed to parse CAFFA output file: {str(e)}")
        
        return data
    
    def _read_int_array(self, f, count: int) -> np.ndarray:
        """Read integer array from binary file"""
        if count <= 0:
            return np.array([])
        return np.fromfile(f, dtype=np.int32, count=count)
    
    def _read_float_array(self, f, count: int) -> np.ndarray:
        """Read float array from binary file"""
        if count <= 0:
            return np.array([])
        return np.fromfile(f, dtype=np.float32, count=count)
    
    def _extract_value(self, line: str) -> float:
        """Extract numeric value from line"""
        try:
            parts = line.split(':')
            if len(parts) > 1:
                return float(parts[1].strip())
        except:
            pass
        return 0.0
    
    def _extract_under_relaxation(self, line: str) -> Tuple[str, float]:
        """Extract under-relaxation factor"""
        if 'U:' in line:
            return 'u', self._extract_value(line)
        elif 'V:' in line:
            return 'v', self._extract_value(line)
        elif 'P:' in line:
            return 'p', self._extract_value(line)
        elif 'T:' in line:
            return 't', self._extract_value(line)
        return None, 0.0
    
    def _extract_blending_factor(self, line: str) -> Tuple[str, float]:
        """Extract blending factor"""
        if 'U:' in line:
            return 'u', self._extract_value(line)
        elif 'V:' in line:
            return 'v', self._extract_value(line)
        elif 'T:' in line:
            return 't', self._extract_value(line)
        return None, 0.0
    
    def _parse_boundary_sections(self, lines: List[str]) -> Dict:
        """Parse boundary condition sections from output"""
        boundaries = {}
        current_section = None
        
        for line in lines:
            if 'SOUTH SIDE:' in line:
                current_section = 'south'
                boundaries[current_section] = []
            elif 'NORTH SIDE:' in line:
                current_section = 'north'
                boundaries[current_section] = []
            elif 'WEST SIDE:' in line:
                current_section = 'west'
                boundaries[current_section] = []
            elif 'EAST SIDE:' in line:
                current_section = 'east'
                boundaries[current_section] = []
            elif current_section and 'ITB' in line or 'JTB' in line:
                try:
                    values = [int(x) for x in line.split()[1:] if x.strip().isdigit()]
                    boundaries[current_section].extend(values)
                except:
                    pass
        
        return boundaries
    
    def _parse_grid_parameters(self, lines: List[str]) -> Dict:
        """Parse grid parameters from output"""
        params = {}
        for line in lines:
            if 'NXA_MAX' in line:
                params['nxa_max'] = self._extract_value(line)
            elif 'NYA_MAX' in line:
                params['nya_max'] = self._extract_value(line)
            elif 'NXYA_MAX' in line:
                params['nxya_max'] = self._extract_value(line)
        return params
    
    def create_mesh_from_grid(self,  dict) -> 'pyvista.StructuredGrid':
        """Create PyVista mesh from grid data"""
        import pyvista as pv
        
        if 'coordinates' not in  'x' not in  'y' not in 
            return None
        
        x = data['coordinates']['x']
        y = data['coordinates']['y']
        
        # Get grid dimensions
        nija = len(x)
        nigr = data['grid_info']['nigr'][-1] if 'grid_info' in  else int(np.sqrt(nija))
        njgr = data['grid_info']['njgr'][-1] if 'grid_info' in  else int(np.sqrt(nija))
        
        # Create 2D structured grid (extend to 3D for visualization)
        ni = nigr
        nj = njgr
        
        if ni * nj != nija:
            # Try to infer dimensions
            ni = int(np.sqrt(nija))
            nj = ni
        
        # Reshape coordinates
        X = x[:ni*nj].reshape((ni, nj))
        Y = y[:ni*nj].reshape((ni, nj))
        Z = np.zeros_like(X)
        
        # Create structured grid
        grid = pv.StructuredGrid(X, Y, Z)
        
        # Add cell volumes as scalars if available
        if 'volumes' in 
            vol = data['volumes'][:ni*nj]
            grid['Volume'] = vol.reshape((ni, nj))
        
        # Add interpolation factors if available
        if 'interpolation_factors' in 
            fx = data['interpolation_factors']['fx'][:ni*nj]
            fy = data['interpolation_factors']['fy'][:ni*nj]
            grid['FX'] = fx.reshape((ni, nj))
            grid['FY'] = fy.reshape((ni, nj))
        
        return grid