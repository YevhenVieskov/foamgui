"""
Extended solver registry with comprehensive OpenFOAM solver support
"""
from typing import Dict, List, Any


class ExtendedSolverRegistry:
    """Comprehensive registry of OpenFOAM solvers"""
    
    def __init__(self):
        self.solvers = self._load_all_solvers()
    
    def _load_all_solvers(self) -> Dict[str, Any]:
        """Load comprehensive solver definitions"""
        return {
            # ===== INCOMPRESSIBLE FLOW =====
            'simpleFoam': {
                'description': 'Steady-state solver for incompressible, turbulent flow',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'nuTilda'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'SpalartAllmaras', 'realizableKE', 'RNGkEpsilon'],
                'time_scheme': 'steadyState',
                'typical_applications': ['External aerodynamics', 'HVAC', 'Mixing'],
                'parallel_capable': True
            },
            'pimpleFoam': {
                'description': 'Transient solver for incompressible, turbulent flow',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'nuTilda'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'SpalartAllmaras', 'LES'],
                'time_scheme': 'transient',
                'typical_applications': ['Transient flows', 'FSI', 'Moving meshes'],
                'parallel_capable': True
            },
            'pisoFoam': {
                'description': 'Transient solver for incompressible flow',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'LES'],
                'time_scheme': 'transient',
                'typical_applications': ['DNS', 'LES simulations'],
                'parallel_capable': True
            },
            'icoFoam': {
                'description': 'Transient solver for incompressible, laminar flow',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['Laminar flows', 'Low Re flows', 'Educational'],
                'parallel_capable': True
            },
            'nonNewtonianIcoFoam': {
                'description': 'Transient solver for incompressible, laminar non-Newtonian flow',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['Blood flow', 'Polymer flows', 'Food processing'],
                'parallel_capable': True
            },
            'porousSimpleFoam': {
                'description': 'Steady-state solver for incompressible flow through porous media',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'steadyState',
                'typical_applications': ['Heat exchangers', 'Filters', 'Porous materials'],
                'parallel_capable': True
            },
            'SRFSimpleFoam': {
                'description': 'Steady-state solver for turbulent flow in rotating frame',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'steadyState',
                'typical_applications': ['Turbomachinery', 'Rotating machinery', 'Mixers'],
                'parallel_capable': True
            },
            'SRFPimpleFoam': {
                'description': 'Transient solver for turbulent flow in rotating frame',
                'category': 'Incompressible',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'transient',
                'typical_applications': ['Turbomachinery transients', 'Pump startups'],
                'parallel_capable': True
            },
            
            # ===== MULTIPHASE FLOW =====
            'interFoam': {
                'description': 'Transient solver for two incompressible, isothermal immiscible fluids',
                'category': 'Multiphase',
                'required_fields': ['U', 'p_rgh', 'alpha.water'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'transient',
                'typical_applications': ['Free surface flows', 'Wave breaking', 'Dam breaks'],
                'parallel_capable': True
            },
            'interPhaseChangeFoam': {
                'description': 'Solver for two incompressible fluids with phase change',
                'category': 'Multiphase',
                'required_fields': ['U', 'p_rgh', 'alpha.water', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Cavitation', 'Boiling', 'Condensation'],
                'parallel_capable': True
            },
            'multiphaseInterFoam': {
                'description': 'Solver for n incompressible, isothermal immiscible fluids',
                'category': 'Multiphase',
                'required_fields': ['U', 'p_rgh'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'transient',
                'typical_applications': ['Oil-water-gas systems', 'Multiple phases'],
                'parallel_capable': True
            },
            'compressibleInterFoam': {
                'description': 'Solver for two compressible, isothermal immiscible fluids',
                'category': 'Multiphase',
                'required_fields': ['U', 'p_rgh', 'alpha.water', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Underwater explosions', 'Gas-liquid systems'],
                'parallel_capable': True
            },
            'twoPhaseEulerFoam': {
                'description': 'Solver for Eulerian two-phase flow',
                'category': 'Multiphase',
                'required_fields': ['U.air', 'U.water', 'p', 'alpha.air'],
                'optional_fields': ['k.air', 'epsilon.air', 'k.water', 'epsilon.water'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Fluidized beds', 'Bubble columns', 'Pneumatic transport'],
                'parallel_capable': True
            },
            
            # ===== HEAT TRANSFER =====
            'buoyantSimpleFoam': {
                'description': 'Steady-state solver for buoyant, turbulent flow',
                'category': 'Heat Transfer',
                'required_fields': ['U', 'p_rgh', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'alphat'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'steadyState',
                'typical_applications': ['Natural convection', 'HVAC', 'Electronics cooling'],
                'parallel_capable': True
            },
            'buoyantPimpleFoam': {
                'description': 'Transient solver for buoyant, turbulent flow',
                'category': 'Heat Transfer',
                'required_fields': ['U', 'p_rgh', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'alphat'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'LES'],
                'time_scheme': 'transient',
                'typical_applications': ['Fire simulation', 'Transient natural convection'],
                'parallel_capable': True
            },
            'chtMultiRegionFoam': {
                'description': 'Solver for conjugate heat transfer with multiple regions',
                'category': 'Heat Transfer',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'transient',
                'typical_applications': ['Conjugate heat transfer', 'Electronics', 'Heat exchangers'],
                'parallel_capable': True
            },
            'chtMultiRegionSimpleFoam': {
                'description': 'Steady-state solver for conjugate heat transfer',
                'category': 'Heat Transfer',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'steadyState',
                'typical_applications': ['Steady CHT', 'Heat sinks', 'Radiators'],
                'parallel_capable': True
            },
            'laplacianFoam': {
                'description': 'Solver for simple Laplacian equation (heat conduction)',
                'category': 'Heat Transfer',
                'required_fields': ['T'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['Heat conduction', 'Diffusion', 'Educational'],
                'parallel_capable': True
            },
            
            # ===== COMPRESSIBLE FLOW =====
            'rhoSimpleFoam': {
                'description': 'Steady-state solver for compressible, turbulent flow',
                'category': 'Compressible',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'alphat'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST'],
                'time_scheme': 'steadyState',
                'typical_applications': ['Subsonic external aero', 'HVAC compressible'],
                'parallel_capable': True
            },
            'rhoPimpleFoam': {
                'description': 'Transient solver for compressible, turbulent flow',
                'category': 'Compressible',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'nut', 'alphat'],
                'turbulence_models': ['kEpsilon', 'kOmega', 'kOmegaSST', 'LES'],
                'time_scheme': 'transient',
                'typical_applications': ['Transient compressible', 'Shock tubes'],
                'parallel_capable': True
            },
            'sonicFoam': {
                'description': 'Transient solver for trans-sonic/supersonic, laminar or turbulent flow',
                'category': 'Compressible',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'transient',
                'typical_applications': ['Supersonic flows', 'Shock waves', 'Nozzles'],
                'parallel_capable': True
            },
            'rhoCentralFoam': {
                'description': 'Density-based compressible flow solver',
                'category': 'Compressible',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['High-speed flows', 'Shock capturing', 'Explosions'],
                'parallel_capable': True
            },
            'pisoCentralFoam': {
                'description': 'Pressure-based compressible flow solver',
                'category': 'Compressible',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Low Mach compressible', 'Acoustics'],
                'parallel_capable': True
            },
            
            # ===== COMBUSTION =====
            'reactingFoam': {
                'description': 'Solver for combustion with chemical reactions',
                'category': 'Combustion',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon', 'omega', 'CH4', 'O2', 'CO2', 'H2O'],
                'turbulence_models': ['kEpsilon', 'kOmega'],
                'time_scheme': 'transient',
                'typical_applications': ['Combustion', 'Chemical reactions', 'Flames'],
                'parallel_capable': True
            },
            'fireFoam': {
                'description': 'Fire and combustion solver',
                'category': 'Combustion',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Fire simulation', 'Pool fires', 'Building fires'],
                'parallel_capable': True
            },
            'coldEngineFoam': {
                'description': 'Solver for cold flow in internal combustion engines',
                'category': 'Combustion',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['IC engines', 'Piston motion', 'Valve flows'],
                'parallel_capable': True
            },
            
            # ===== PARTICLE TRACKING =====
            'icoUncoupledKinematicParcelFoam': {
                'description': 'Transient solver for particle tracking in incompressible flow',
                'category': 'Particle Tracking',
                'required_fields': ['U', 'p'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Spray modeling', 'Particle dispersion', 'Aerosols'],
                'parallel_capable': True
            },
            'sprayFoam': {
                'description': 'Transient solver for spray and particle flows',
                'category': 'Particle Tracking',
                'required_fields': ['U', 'p', 'T'],
                'optional_fields': ['k', 'epsilon'],
                'turbulence_models': ['kEpsilon'],
                'time_scheme': 'transient',
                'typical_applications': ['Fuel injection', 'Atomization', 'Spray drying'],
                'parallel_capable': True
            },
            
            # ===== SOLID MECHANICS =====
            'solidDisplacementFoam': {
                'description': 'Transient segregated finite-volume solver for solid dynamics',
                'category': 'Solid Mechanics',
                'required_fields': ['D'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['Structural analysis', 'Elasticity', 'FSI'],
                'parallel_capable': True
            },
            'solidEquilibriumDisplacementFoam': {
                'description': 'Steady-state solver for solid mechanics',
                'category': 'Solid Mechanics',
                'required_fields': ['D'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'steadyState',
                'typical_applications': ['Static structural', 'Stress analysis'],
                'parallel_capable': True
            },
            
            # ===== ELECTROMAGNETICS =====
            'electrostaticFoam': {
                'description': 'Solver for electrostatics',
                'category': 'Electromagnetics',
                'required_fields': ['phi'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'steadyState',
                'typical_applications': ['Electrostatics', 'Capacitors', 'Electric fields'],
                'parallel_capable': True
            },
            'magneticFoam': {
                'description': 'Solver for magnetostatics',
                'category': 'Electromagnetics',
                'required_fields': ['psi'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'steadyState',
                'typical_applications': ['Magnetostatics', 'Inductors', 'Magnetic fields'],
                'parallel_capable': True
            },
            
            # ===== SPECIAL PURPOSE =====
            'potentialFoam': {
                'description': 'Potential flow solver',
                'category': 'Special',
                'required_fields': ['U', 'p'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'steadyState',
                'typical_applications': ['Initial conditions', 'Inviscid flow', 'Quick estimates'],
                'parallel_capable': True
            },
            'scalarTransportFoam': {
                'description': 'Solver for passive scalar transport',
                'category': 'Special',
                'required_fields': ['U', 'T'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'transient',
                'typical_applications': ['Tracer transport', 'Pollution dispersion', 'Species transport'],
                'parallel_capable': True
            },
            'adjointShapeOptimizationFoam': {
                'description': 'Adjoint solver for shape optimization',
                'category': 'Special',
                'required_fields': ['U', 'p', 'Ua', 'pa'],
                'optional_fields': [],
                'turbulence_models': [],
                'time_scheme': 'steadyState',
                'typical_applications': ['Shape optimization', 'Design', 'Topology optimization'],
                'parallel_capable': True
            }
        }
    
    def get_solver_list(self) -> List[str]:
        """Get list of available solvers"""
        return sorted(self.solvers.keys())
    
    def get_solvers_by_category(self) -> Dict[str, List[str]]:
        """Get solvers organized by category"""
        categories = {}
        for name, info in self.solvers.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
        return categories
    
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
    
    def get_recommended_settings(self, solver_name: str) -> Dict[str, Any]:
        """Get recommended settings for a solver"""
        solver_info = self.get_solver_info(solver_name)
        
        if solver_info.get('time_scheme') == 'steadyState':
            return {
                'ddtSchemes': 'steadyState',
                'nNonOrthogonalCorrectors': 0,
                'nCorrectors': 2,
                'pRefCell': 0,
                'pRefValue': 0
            }
        else:
            return {
                'ddtSchemes': 'Euler',
                'maxCo': 1.0,
                'maxDeltaT': 1.0,
                'nOuterCorrectors': 1,
                'nCorrectors': 2,
                'nNonOrthogonalCorrectors': 0
            }
    
    def search_solvers(self, query: str) -> List[str]:
        """Search solvers by name or description"""
        query = query.lower()
        results = []
        
        for name, info in self.solvers.items():
            if (query in name.lower() or 
                query in info['description'].lower() or
                any(query in app.lower() for app in info['typical_applications'])):
                results.append(name)
        
        return results
