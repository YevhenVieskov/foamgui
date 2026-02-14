"""
Comprehensive mesh quality checking module
"""
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import re


class MeshQualityChecker:
    """Advanced mesh quality analysis"""
    
    # Quality criteria standards
    QUALITY_CRITERIA = {
        'excellent': {
            'maxNonOrtho': 45,
            'maxSkewness': 2,
            'maxAspectRatio': 4,
            'minVolume': 1e-15,
            'minFaceArea': 1e-15,
            'minPyramidVolume': 1e-13
        },
        'good': {
            'maxNonOrtho': 65,
            'maxSkewness': 4,
            'maxAspectRatio': 10,
            'minVolume': 1e-16,
            'minFaceArea': 1e-16,
            'minPyramidVolume': 1e-14
        },
        'acceptable': {
            'maxNonOrtho': 70,
            'maxSkewness': 6,
            'maxAspectRatio': 20,
            'minVolume': 1e-17,
            'minFaceArea': 1e-17,
            'minPyramidVolume': 1e-15
        },
        'poor': {
            'maxNonOrtho': 80,
            'maxSkewness': 10,
            'maxAspectRatio': 50,
            'minVolume': 1e-18,
            'minFaceArea': 1e-18,
            'minPyramidVolume': 1e-16
        }
    }
    
    def __init__(self, case_path: str):
        self.case_path = Path(case_path)
        self.mesh_stats = {}
        self.quality_metrics = {}
        
    def run_check_mesh(self) -> Dict[str, any]:
        """Run OpenFOAM checkMesh utility"""
        try:
            result = subprocess.run(
                ['checkMesh', '-case', str(self.case_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self._parse_checkmesh_output(result.stdout)
            return self.mesh_stats
            
        except subprocess.TimeoutExpired:
            return {'error': 'checkMesh timeout'}
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_checkmesh_output(self, output: str):
        """Parse checkMesh output"""
        self.mesh_stats = {
            'cells': 0,
            'faces': 0,
            'points': 0,
            'internal_faces': 0,
            'boundary_faces': 0,
            'non_orthogonality': {'max': 0, 'average': 0},
            'skewness': {'max': 0, 'average': 0},
            'aspect_ratio': {'max': 0, 'average': 0},
            'volume': {'min': 0, 'max': 0, 'total': 0},
            'failed_checks': []
        }
        
        # Parse cell count
        match = re.search(r'cells:\s*(\d+)', output)
        if match:
            self.mesh_stats['cells'] = int(match.group(1))
        
        # Parse face count
        match = re.search(r'faces:\s*(\d+)', output)
        if match:
            self.mesh_stats['faces'] = int(match.group(1))
        
        # Parse point count
        match = re.search(r'points:\s*(\d+)', output)
        if match:
            self.mesh_stats['points'] = int(match.group(1))
        
        # Parse non-orthogonality
        match = re.search(r'Max non-orthogonality = ([\d.]+) average = ([\d.]+)', output)
        if match:
            self.mesh_stats['non_orthogonality']['max'] = float(match.group(1))
            self.mesh_stats['non_orthogonality']['average'] = float(match.group(2))
        
        # Parse skewness
        match = re.search(r'Max skewness = ([\d.]+) average = ([\d.]+)', output)
        if match:
            self.mesh_stats['skewness']['max'] = float(match.group(1))
            self.mesh_stats['skewness']['average'] = float(match.group(2))
        
        # Check for failed tests
        if 'FAIL' in output or 'Failed' in output:
            for line in output.split('\n'):
                if 'FAIL' in line or 'Failed' in line:
                    self.mesh_stats['failed_checks'].append(line.strip())
    
    def assess_quality(self) -> Dict[str, any]:
        """Assess overall mesh quality"""
        if not self.mesh_stats:
            self.run_check_mesh()
        
        assessment = {
            'overall_grade': 'unknown',
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'scores': {}
        }
        
        # Evaluate non-orthogonality
        non_ortho = self.mesh_stats.get('non_orthogonality', {}).get('max', 0)
        if non_ortho <= self.QUALITY_CRITERIA['excellent']['maxNonOrtho']:
            assessment['scores']['non_orthogonality'] = 'excellent'
        elif non_ortho <= self.QUALITY_CRITERIA['good']['maxNonOrtho']:
            assessment['scores']['non_orthogonality'] = 'good'
        elif non_ortho <= self.QUALITY_CRITERIA['acceptable']['maxNonOrtho']:
            assessment['scores']['non_orthogonality'] = 'acceptable'
            assessment['warnings'].append(f'Non-orthogonality ({non_ortho:.1f}) is acceptable but not ideal')
        else:
            assessment['scores']['non_orthogonality'] = 'poor'
            assessment['issues'].append(f'High non-orthogonality ({non_ortho:.1f}) may cause convergence issues')
            assessment['recommendations'].append('Refine mesh or improve cell quality')
        
        # Evaluate skewness
        skewness = self.mesh_stats.get('skewness', {}).get('max', 0)
        if skewness <= self.QUALITY_CRITERIA['excellent']['maxSkewness']:
            assessment['scores']['skewness'] = 'excellent'
        elif skewness <= self.QUALITY_CRITERIA['good']['maxSkewness']:
            assessment['scores']['skewness'] = 'good'
        elif skewness <= self.QUALITY_CRITERIA['acceptable']['maxSkewness']:
            assessment['scores']['skewness'] = 'acceptable'
        else:
            assessment['scores']['skewness'] = 'poor'
            assessment['issues'].append(f'High skewness ({skewness:.1f}) detected')
        
        # Check for failed mesh checks
        if self.mesh_stats.get('failed_checks'):
            assessment['issues'].extend(self.mesh_stats['failed_checks'])
            assessment['overall_grade'] = 'failed'
        else:
            # Determine overall grade
            scores = list(assessment['scores'].values())
            if all(s in ['excellent', 'good'] for s in scores):
                assessment['overall_grade'] = 'excellent'
            elif all(s in ['excellent', 'good', 'acceptable'] for s in scores):
                assessment['overall_grade'] = 'good'
            elif 'poor' in scores:
                assessment['overall_grade'] = 'poor'
            else:
                assessment['overall_grade'] = 'acceptable'
        
        return assessment
    
    def calculate_advanced_metrics(self) -> Dict[str, any]:
        """Calculate advanced mesh quality metrics"""
        metrics = {
            'equiangle_skewness': self._calculate_equiangle_skewness(),
            'equivolume_skewness': self._calculate_equivolume_skewness(),
            'cell_volume_ratio': self._calculate_volume_ratio(),
            'face_area_ratio': self._calculate_area_ratio(),
            'cell_count_distribution': self._analyze_cell_distribution()
        }
        
        return metrics
    
    def _calculate_equiangle_skewness(self) -> float:
        """Calculate equiangle skewness (simplified)"""
        # This is a simplified calculation
        # Full implementation would read actual mesh data
        return 0.0
    
    def _calculate_equivolume_skewness(self) -> float:
        """Calculate equivolume skewness (simplified)"""
        return 0.0
    
    def _calculate_volume_ratio(self) -> float:
        """Calculate max/min cell volume ratio"""
        vol = self.mesh_stats.get('volume', {})
        if vol.get('min', 0) > 0:
            return vol.get('max', 1) / vol.get('min', 1)
        return 0.0
    
    def _calculate_area_ratio(self) -> float:
        """Calculate face area ratio"""
        # Simplified calculation
        return 1.0
    
    def _analyze_cell_distribution(self) -> Dict[str, int]:
        """Analyze cell type distribution"""
        return {
            'hexahedra': self.mesh_stats.get('cells', 0),
            'prisms': 0,
            'pyramids': 0,
            'tetrahedra': 0
        }
    
    def generate_quality_report(self) -> str:
        """Generate comprehensive quality report"""
        if not self.mesh_stats:
            self.run_check_mesh()
        
        assessment = self.assess_quality()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              MESH QUALITY ASSESSMENT REPORT                   ║
╚══════════════════════════════════════════════════════════════╝

MESH STATISTICS
{'─' * 60}
Cells:              {self.mesh_stats.get('cells', 'N/A'):>12}
Faces:              {self.mesh_stats.get('faces', 'N/A'):>12}
Points:             {self.mesh_stats.get('points', 'N/A'):>12}

QUALITY METRICS
{'─' * 60}
Non-Orthogonality:  
  Max:              {self.mesh_stats.get('non_orthogonality', {}).get('max', 0):>12.2f}
  Average:          {self.mesh_stats.get('non_orthogonality', {}).get('average', 0):>12.2f}
  Grade:            {assessment['scores'].get('non_orthogonality', 'N/A'):>12}

Skewness:
  Max:              {self.mesh_stats.get('skewness', {}).get('max', 0):>12.2f}
  Average:          {self.mesh_stats.get('skewness', {}).get('average', 0):>12.2f}
  Grade:            {assessment['scores'].get('skewness', 'N/A'):>12}

OVERALL ASSESSMENT
{'─' * 60}
Overall Grade:      {assessment['overall_grade'].upper():>12}

"""
        
        if assessment['issues']:
            report += f"\nISSUES:\n"
            for issue in assessment['issues']:
                report += f"  ❌ {issue}\n"
        
        if assessment['warnings']:
            report += f"\nWARNINGS:\n"
            for warning in assessment['warnings']:
                report += f"  ⚠️  {warning}\n"
        
        if assessment['recommendations']:
            report += f"\nRECOMMENDATIONS:\n"
            for rec in assessment['recommendations']:
                report += f"  💡 {rec}\n"
        
        report += f"\n{'═' * 60}\n"
        
        return report
    
    def export_report(self, output_file: str = None):
        """Export quality report to file"""
        if output_file is None:
            output_file = self.case_path / 'meshQuality.report'
        
        report = self.generate_quality_report()
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        return output_file
    
    def visualize_quality(self) -> Dict[str, any]:
        """Prepare data for quality visualization"""
        return {
            'non_orthogonality': {
                'max': self.mesh_stats.get('non_orthogonality', {}).get('max', 0),
                'average': self.mesh_stats.get('non_orthogonality', {}).get('average', 0),
                'threshold_excellent': self.QUALITY_CRITERIA['excellent']['maxNonOrtho'],
                'threshold_good': self.QUALITY_CRITERIA['good']['maxNonOrtho'],
                'threshold_acceptable': self.QUALITY_CRITERIA['acceptable']['maxNonOrtho']
            },
            'skewness': {
                'max': self.mesh_stats.get('skewness', {}).get('max', 0),
                'average': self.mesh_stats.get('skewness', {}).get('average', 0),
                'threshold_excellent': self.QUALITY_CRITERIA['excellent']['maxSkewness'],
                'threshold_good': self.QUALITY_CRITERIA['good']['maxSkewness'],
                'threshold_acceptable': self.QUALITY_CRITERIA['acceptable']['maxSkewness']
            }
        }
    
    def compare_with_standards(self, standard: str = 'good') -> Dict[str, bool]:
        """Compare mesh quality with standards"""
        if standard not in self.QUALITY_CRITERIA:
            standard = 'good'
        
        criteria = self.QUALITY_CRITERIA[standard]
        
        comparison = {
            'non_orthogonality': self.mesh_stats.get('non_orthogonality', {}).get('max', 999) <= criteria['maxNonOrtho'],
            'skewness': self.mesh_stats.get('skewness', {}).get('max', 999) <= criteria['maxSkewness'],
            'meets_standard': True
        }
        
        comparison['meets_standard'] = all([comparison['non_orthogonality'], comparison['skewness']])
        
        return comparison
    
    def suggest_improvements(self) -> List[str]:
        """Suggest mesh improvements"""
        suggestions = []
        
        assessment = self.assess_quality()
        
        if assessment['scores'].get('non_orthogonality') in ['poor', 'acceptable']:
            suggestions.append("Reduce non-orthogonality by:")
            suggestions.append("  - Using simpler blocking strategy")
            suggestions.append("  - Aligning blocks with flow direction")
            suggestions.append("  - Increasing mesh resolution in critical regions")
        
        if assessment['scores'].get('skewness') in ['poor', 'acceptable']:
            suggestions.append("Reduce skewness by:")
            suggestions.append("  - Improving vertex placement")
            suggestions.append("  - Using edge grading")
            suggestions.append("  - Avoiding extreme cell aspect ratios")
        
        if self.mesh_stats.get('cells', 0) < 1000:
            suggestions.append("Consider increasing mesh resolution for better accuracy")
        
        if self.mesh_stats.get('cells', 0) > 10000000:
            suggestions.append("Very large mesh - consider mesh coarsening for faster simulations")
        
        return suggestions


class MeshQualityVisualizer:
    """Visualize mesh quality metrics"""
    
    def __init__(self, quality_checker: MeshQualityChecker):
        self.checker = quality_checker
    
    def create_quality_histogram(self):
        """Create histogram of quality metrics"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # Non-orthogonality
        data = self.checker.visualize_quality()
        non_ortho = data['non_orthogonality']
        
        ax = axes[0]
        ax.barh(['Max', 'Average'], 
                [non_ortho['max'], non_ortho['average']],
                color=['red', 'orange'])
        ax.axvline(non_ortho['threshold_excellent'], color='green', linestyle='--', label='Excellent')
        ax.axvline(non_ortho['threshold_good'], color='blue', linestyle='--', label='Good')
        ax.axvline(non_ortho['threshold_acceptable'], color='orange', linestyle='--', label='Acceptable')
        ax.set_xlabel('Non-Orthogonality (degrees)')
        ax.set_title('Non-Orthogonality Assessment')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Skewness
        skewness = data['skewness']
        
        ax = axes[1]
        ax.barh(['Max', 'Average'],
                [skewness['max'], skewness['average']],
                color=['red', 'orange'])
        ax.axvline(skewness['threshold_excellent'], color='green', linestyle='--', label='Excellent')
        ax.axvline(skewness['threshold_good'], color='blue', linestyle='--', label='Good')
        ax.axvline(skewness['threshold_acceptable'], color='orange', linestyle='--', label='Acceptable')
        ax.set_xlabel('Skewness')
        ax.set_title('Skewness Assessment')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_quality_radar_chart(self):
        """Create radar chart of quality metrics"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Prepare data (normalized scores)
        categories = ['Non-Orthogonality', 'Skewness', 'Volume Ratio', 
                     'Aspect Ratio', 'Cell Count']
        
        # Normalize values (0-100 scale, 100 is best)
        values = [80, 85, 90, 75, 85]  # Placeholder values
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values, 'o-', linewidth=2, color='blue', label='Current Mesh')
        ax.fill(angles, values, alpha=0.25, color='blue')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('Mesh Quality Assessment', size=16, pad=20)
        ax.legend(loc='upper right')
        ax.grid(True)
        
        return fig
