"""Solver registry for OpenFOAM solvers"""
import json
from pathlib import Path
from typing import Dict, List, Any


class SolverRegistry:
    """Registry of OpenFOAM solvers with their configurations"""
    
    def __init__(self):
        self.solvers = self._load_solvers()
    
    def _load_solvers(self) -> Dict[str, Any]:
        """Load solver definitions"""
        return {
            'simpleFoam': {
                'description': 'Steady-state solver for incompressible, turbulent flow',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'SpalartAllmaras'],
                'time_scheme': 'steadyState'
            },
            'pimpleFoam': {
                'description': 'Transient solver for incompressible, turbulent flow',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'SpalartAllmaras', 'LES'],
                'time_scheme': 'transient'
            },
            'icoFoam': {
                'description': 'Transient solver for incompressible, laminar flow',
                'required_fields': ['U', 'p'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient'
            },
            'interFoam': {
                'description': 'Transient solver for two incompressible, isothermal immiscible fluids',
                'required_fields': ['U', 'p', 'alpha.water'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'transient'
            },
            'buoyantSimpleFoam': {
                'description': 'Steady-state solver for buoyant, turbulent flow',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'steadyState'
            },
            'buoyantPimpleFoam': {
                'description': 'Transient solver for buoyant, turbulent flow',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'LES'],
                'time_scheme': 'transient'
            },
            'rhoSimpleFoam': {
                'description': 'Steady-state solver for compressible, turbulent flow',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'steadyState'
            },
            'sonicFoam': {
                'description': 'Transient solver for compressible flow',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'transient'
            }
        }
    
    def get_solver_list(self) -> List[str]:
        """Get list of available solvers"""
        return list(self.solvers.keys())
    
    def get_solver_info(self, solver_name: str) -> Dict[str, Any]:
        """Get information about a specific solver"""
        return self.solvers.get(solver_name, {})
    
    def validate_solver_setup(self, solver_name: str, fields: List[str]) -> tuple[bool, List[str]]:
        """Validate solver setup
        
        Returns:
            (is_valid, missing_fields)
        """
        solver_info = self.get_solver_info(solver_name)
        if not solver_info:
            return False, [f"Unknown solver: {solver_name}"]
        
        required = solver_info.get('required_fields', [])
        missing = [field for field in required if field not in fields]
        
        return len(missing) == 0, missing
