"""
Functional tests for OpenFOAM GUI
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Mock PyQt6 if not available for testing
try:
    from PyQt6.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 not available - skipping GUI tests")


class TestCaseWorkflow(unittest.TestCase):
    """Test complete case workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        from core.config import AppConfig
        from core.case_manager import CaseManager
        
        self.config = AppConfig()
        self.case_manager = CaseManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete case creation and configuration workflow"""
        # Step 1: Create case
        case_data = {
            'name': 'workflowTest',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        
        case_path = self.case_manager.create_case(case_data)
        self.assertIsNotNone(case_path)
        
        # Step 2: Verify case structure
        case_dir = Path(case_path)
        self.assertTrue((case_dir / 'constant').exists())
        self.assertTrue((case_dir / 'system').exists())
        self.assertTrue((case_dir / '0').exists())
        
        # Step 3: Verify configuration files
        self.assertTrue((case_dir / 'system' / 'controlDict').exists())
        self.assertTrue((case_dir / 'system' / 'fvSchemes').exists())
        self.assertTrue((case_dir / 'system' / 'fvSolution').exists())
        
        # Step 4: Load case
        self.case_manager.load_case(case_path)
        self.assertEqual(self.case_manager.current_case, case_path)
        
        # Step 5: Save case
        self.case_manager.save_case(case_path)
        self.assertTrue((case_dir / '.metadata.json').exists())


class TestMeshGeneration(unittest.TestCase):
    """Test mesh generation workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        from core.config import AppConfig
        from core.case_manager import CaseManager
        
        self.config = AppConfig()
        self.case_manager = CaseManager(self.config)
        
        # Create test case
        case_data = {
            'name': 'meshTest',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        self.case_path = self.case_manager.create_case(case_data)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_blockmesh_dict_creation(self):
        """Test blockMeshDict file creation"""
        case_dir = Path(self.case_path)
        blockmesh_file = case_dir / 'system' / 'blockMeshDict'
        
        # Create simple blockMeshDict
        blockmesh_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

convertToMeters 1;

vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 1)
    (1 0 1)
    (1 1 1)
    (0 1 1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
);
"""
        
        with open(blockmesh_file, 'w') as f:
            f.write(blockmesh_content)
        
        self.assertTrue(blockmesh_file.exists())
    
    def test_mesh_directory_structure(self):
        """Test mesh directory structure"""
        case_dir = Path(self.case_path)
        polymesh_dir = case_dir / 'constant' / 'polyMesh'
        
        self.assertTrue(polymesh_dir.exists())


class TestSolverConfiguration(unittest.TestCase):
    """Test solver configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        from core.config import AppConfig
        from core.case_manager import CaseManager
        from solvers.solver_registry import SolverRegistry
        
        self.config = AppConfig()
        self.case_manager = CaseManager(self.config)
        self.registry = SolverRegistry()
        
        # Create test case
        case_data = {
            'name': 'solverTest',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        self.case_path = self.case_manager.create_case(case_data)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_solver_field_validation(self):
        """Test solver field requirements validation"""
        # Test simpleFoam
        is_valid, missing = self.registry.validate_solver_setup('simpleFoam', ['U', 'p'])
        self.assertTrue(is_valid)
        
        # Test interFoam
        is_valid, missing = self.registry.validate_solver_setup('interFoam', ['U', 'p'])
        self.assertFalse(is_valid)
        self.assertIn('alpha.water', missing)
        
        # Test with all required fields
        is_valid, missing = self.registry.validate_solver_setup('interFoam', ['U', 'p', 'alpha.water'])
        self.assertTrue(is_valid)
    
    def test_control_dict_parsing(self):
        """Test controlDict parsing"""
        case_dir = Path(self.case_path)
        control_dict = case_dir / 'system' / 'controlDict'
        
        # Read and verify controlDict
        with open(control_dict, 'r') as f:
            content = f.read()
        
        self.assertIn('application', content)
        self.assertIn('simpleFoam', content)
        self.assertIn('startTime', content)
        self.assertIn('endTime', content)


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestGUIComponents(unittest.TestCase):
    """Test GUI components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication"""
        if PYQT_AVAILABLE:
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt6 not available")
        
        self.temp_dir = tempfile.mkdtemp()
        
        from core.config import AppConfig
        self.config = AppConfig()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_main_window_creation(self):
        """Test main window creation"""
        from core.main_window import MainWindow
        
        window = MainWindow(self.config)
        self.assertIsNotNone(window)
        
        # Verify main components exist
        self.assertIsNotNone(window.case_tree)
        self.assertIsNotNone(window.mesh_panel)
        self.assertIsNotNone(window.solver_config)
        self.assertIsNotNone(window.residual_monitor)
        self.assertIsNotNone(window.contour_viewer)
    
    def test_case_tree_widget(self):
        """Test case tree widget"""
        from widgets.case_tree import CaseTreeWidget
        
        tree = CaseTreeWidget()
        self.assertIsNotNone(tree)
    
    def test_solver_config_widget(self):
        """Test solver configuration widget"""
        from widgets.solver_config import SolverConfigWidget
        
        widget = SolverConfigWidget(self.config)
        self.assertIsNotNone(widget)
        
        # Verify combo boxes exist
        self.assertIsNotNone(widget.solver_combo)
    
    def test_mesh_panel_widget(self):
        """Test mesh panel widget"""
        from widgets.mesh_panel import MeshPanelWidget
        
        widget = MeshPanelWidget(self.config)
        self.assertIsNotNone(widget)


class TestResidualMonitoring(unittest.TestCase):
    """Test residual monitoring functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_residual_log_parsing(self):
        """Test parsing solver residual logs"""
        # Create sample log file
        log_content = """Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.999, Final residual = 0.001, No Iterations 10
smoothSolver:  Solving for Uy, Initial residual = 0.998, Final residual = 0.002, No Iterations 10
smoothSolver:  Solving for Uz, Initial residual = 0.997, Final residual = 0.003, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.995, Final residual = 0.005, No Iterations 5

Time = 2
smoothSolver:  Solving for Ux, Initial residual = 0.5, Final residual = 0.0001, No Iterations 8
smoothSolver:  Solving for Uy, Initial residual = 0.4, Final residual = 0.0002, No Iterations 8
smoothSolver:  Solving for Uz, Initial residual = 0.3, Final residual = 0.0003, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.2, Final residual = 0.0005, No Iterations 4
"""
        
        log_file = Path(self.temp_dir) / 'log.simpleFoam'
        with open(log_file, 'w') as f:
            f.write(log_content)
        
        # Parse log
        import re
        residuals = {}
        iterations = []
        
        with open(log_file, 'r') as f:
            current_time = None
            for line in f:
                time_match = re.search(r'Time\s*=\s*(\d+)', line)
                if time_match:
                    current_time = int(time_match.group(1))
                    if current_time not in iterations:
                        iterations.append(current_time)
                    continue
                
                residual_match = re.search(
                    r'Solving for (\w+),.*Initial residual = ([\d.e+-]+)',
                    line
                )
                
                if residual_match:
                    field = residual_match.group(1)
                    residual = float(residual_match.group(2))
                    
                    if field not in residuals:
                        residuals[field] = []
                    residuals[field].append(residual)
        
        # Verify parsing
        self.assertEqual(len(iterations), 2)
        self.assertIn('Ux', residuals)
        self.assertIn('p', residuals)
        self.assertEqual(len(residuals['Ux']), 2)
        self.assertAlmostEqual(residuals['Ux'][0], 0.999, places=3)
        self.assertAlmostEqual(residuals['Ux'][1], 0.5, places=3)


def run_functional_tests():
    """Run all functional tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCaseWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestMeshGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestSolverConfiguration))
    
    if PYQT_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestGUIComponents))
    
    suite.addTests(loader.loadTestsFromTestCase(TestResidualMonitoring))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_functional_tests()
    sys.exit(0 if success else 1)
