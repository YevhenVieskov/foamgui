"""
OpenFOAM case management
"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import json


class CaseManager:
    """Manages OpenFOAM cases"""
    
    def __init__(self, config):
        self.config = config
        self.current_case = None
        self.solver_process = None
        
    def create_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """Create new OpenFOAM case
        
        Args:
            case_data: Dictionary containing:
                - name: Case name
                - path: Parent directory path
                - solver: Solver type
                - dimension: 2D or 3D
                - template: Optional template case
        
        Returns:
            Path to created case or None if failed
        """
        try:
            case_path = Path(case_data['path']) / case_data['name']
            case_path.mkdir(parents=True, exist_ok=False)
            
            # Create standard OpenFOAM directory structure
            (case_path / 'constant').mkdir()
            (case_path / 'constant' / 'polyMesh').mkdir()
            (case_path / 'system').mkdir()
            (case_path / '0').mkdir()
            
            # Create controlDict
            self._create_control_dict(case_path, case_data)
            
            # Create fvSchemes
            self._create_fv_schemes(case_path, case_data['solver'])
            
            # Create fvSolution
            self._create_fv_solution(case_path, case_data['solver'])
            
            # Copy template if provided
            if 'template' in case_data and case_data['template']:
                self._copy_template(case_data['template'], case_path)
            
            return str(case_path)
            
        except Exception as e:
            print(f"Error creating case: {e}")
            return None
    
    def load_case(self, case_path: str):
        """Load existing OpenFOAM case"""
        case_path = Path(case_path)
        
        if not case_path.exists():
            raise FileNotFoundError(f"Case not found: {case_path}")
        
        # Verify it's a valid OpenFOAM case
        required_dirs = ['constant', 'system']
        for dir_name in required_dirs:
            if not (case_path / dir_name).exists():
                raise ValueError(f"Invalid OpenFOAM case: missing {dir_name} directory")
        
        self.current_case = str(case_path)
        
        # Read case metadata
        metadata_file = case_path / '.metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.case_metadata = json.load(f)
        else:
            self.case_metadata = self._extract_metadata(case_path)
    
    def save_case(self, case_path: str):
        """Save case metadata"""
        if not self.case_metadata:
            return
        
        metadata_file = Path(case_path) / '.metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(self.case_metadata, f, indent=2)
    
    def run_solver(self, case_path: str):
        """Run OpenFOAM solver"""
        case_path = Path(case_path)
        solver = self.case_metadata.get('solver', 'simpleFoam')
        
        # Source OpenFOAM environment and run solver
        openfoam_path = self.config.get('openfoam_path')
        
        cmd = f'''
        cd {case_path} && \
        source {openfoam_path}/etc/bashrc && \
        {solver} > log.{solver} 2>&1
        '''
        
        self.solver_process = subprocess.Popen(
            cmd,
            shell=True,
            executable='/bin/bash'
        )
    
    def stop_solver(self):
        """Stop running solver"""
        if self.solver_process:
            self.solver_process.terminate()
            self.solver_process.wait()
            self.solver_process = None
    
    def run_mesher(self, case_path: str, mesher: str = 'blockMesh'):
        """Run mesh generator
        
        Args:
            case_path: Path to case
            mesher: Mesher type (blockMesh, snappyHexMesh, cfMesh)
        """
        case_path = Path(case_path)
        openfoam_path = self.config.get('openfoam_path')
        
        cmd = f'''
        cd {case_path} && \
        source {openfoam_path}/etc/bashrc && \
        {mesher} > log.{mesher} 2>&1
        '''
        
        subprocess.run(cmd, shell=True, executable='/bin/bash')
    
    def _create_control_dict(self, case_path: Path, case_data: Dict[str, Any]):
        """Create controlDict file"""
        control_dict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     {case_data['solver']};

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
"""
        
        with open(case_path / 'system' / 'controlDict', 'w') as f:
            f.write(control_dict)
    
    def _create_fv_schemes(self, case_path: Path, solver: str):
        """Create fvSchemes file"""
        fv_schemes = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss upwind;
    div(phi,k)      bounded Gauss upwind;
    div(phi,epsilon) bounded Gauss upwind;
    div(phi,omega)  bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method meshWave;
}

// ************************************************************************* //
"""
        
        with open(case_path / 'system' / 'fvSchemes', 'w') as f:
            f.write(fv_schemes)
    
    def _create_fv_solution(self, case_path: Path, solver: str):
        """Create fvSolution file"""
        fv_solution = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    k
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    epsilon
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    omega
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      yes;

    residualControl
    {
        p               1e-4;
        U               1e-4;
        "(k|epsilon|omega)" 1e-4;
    }
}

relaxationFactors
{
    equations
    {
        U               0.9;
        ".*"            0.9;
    }
}

// ************************************************************************* //
"""
        
        with open(case_path / 'system' / 'fvSolution', 'w') as f:
            f.write(fv_solution)
    
    def _copy_template(self, template_path: str, case_path: Path):
        """Copy template case"""
        template = Path(template_path)
        if template.exists():
            for item in template.iterdir():
                if item.is_dir():
                    shutil.copytree(item, case_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, case_path / item.name)
    
    def _extract_metadata(self, case_path: Path) -> Dict[str, Any]:
        """Extract case metadata from existing case"""
        metadata = {
            'name': case_path.name,
            'path': str(case_path.parent),
            'solver': 'simpleFoam',  # Default
            'dimension': '3D'
        }
        
        # Try to read solver from controlDict
        control_dict = case_path / 'system' / 'controlDict'
        if control_dict.exists():
            with open(control_dict, 'r') as f:
                for line in f:
                    if 'application' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            metadata['solver'] = parts[1].strip(';')
                        break
        
        return metadata
