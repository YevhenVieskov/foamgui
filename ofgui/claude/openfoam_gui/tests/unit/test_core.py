"""
Unit tests for OpenFOAM GUI core functionality
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.config import AppConfig
from core.case_manager import CaseManager
from solvers.solver_registry import SolverRegistry


class TestAppConfig(unittest.TestCase):
    """Test application configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / 'test_config.json'
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_creation(self):
        """Test configuration creation"""
        config = AppConfig(str(self.config_file))
        self.assertIsNotNone(config.config)
        self.assertIn('openfoam_path', config.config)
    
    def test_config_get_set(self):
        """Test configuration get/set"""
        config = AppConfig(str(self.config_file))
        
        # Test set
        config.set('test_key', 'test_value')
        self.assertEqual(config.get('test_key'), 'test_value')
        
        # Test default
        self.assertEqual(config.get('nonexistent', 'default'), 'default')
    
    def test_config_persistence(self):
        """Test configuration persistence"""
        config1 = AppConfig(str(self.config_file))
        config1.set('persistent_key', 'persistent_value')
        
        # Create new config instance
        config2 = AppConfig(str(self.config_file))
        self.assertEqual(config2.get('persistent_key'), 'persistent_value')
    
    def test_recent_cases(self):
        """Test recent cases management"""
        config = AppConfig(str(self.config_file))
        
        config.add_recent_case('/path/to/case1')
        config.add_recent_case('/path/to/case2')
        config.add_recent_case('/path/to/case3')
        
        recent = config.get('recent_cases')
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0], '/path/to/case3')  # Most recent first
        
        # Test duplicate
        config.add_recent_case('/path/to/case1')
        recent = config.get('recent_cases')
        self.assertEqual(len(recent), 3)  # No duplicates
        self.assertEqual(recent[0], '/path/to/case1')


class TestCaseManager(unittest.TestCase):
    """Test case manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_case(self):
        """Test case creation"""
        case_manager = CaseManager(self.config)
        
        case_data = {
            'name': 'testCase',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        
        case_path = case_manager.create_case(case_data)
        self.assertIsNotNone(case_path)
        
        # Verify directory structure
        case_dir = Path(case_path)
        self.assertTrue(case_dir.exists())
        self.assertTrue((case_dir / 'constant').exists())
        self.assertTrue((case_dir / 'system').exists())
        self.assertTrue((case_dir / '0').exists())
        
        # Verify files
        self.assertTrue((case_dir / 'system' / 'controlDict').exists())
        self.assertTrue((case_dir / 'system' / 'fvSchemes').exists())
        self.assertTrue((case_dir / 'system' / 'fvSolution').exists())
    
    def test_load_case(self):
        """Test case loading"""
        case_manager = CaseManager(self.config)
        
        # Create case first
        case_data = {
            'name': 'testCase',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        case_path = case_manager.create_case(case_data)
        
        # Load case
        case_manager.load_case(case_path)
        self.assertEqual(case_manager.current_case, case_path)
    
    def test_load_invalid_case(self):
        """Test loading invalid case"""
        case_manager = CaseManager(self.config)
        
        with self.assertRaises(FileNotFoundError):
            case_manager.load_case('/nonexistent/path')
    
    def test_save_case(self):
        """Test case saving"""
        case_manager = CaseManager(self.config)
        
        # Create and load case
        case_data = {
            'name': 'testCase',
            'path': self.temp_dir,
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        case_path = case_manager.create_case(case_data)
        case_manager.load_case(case_path)
        
        # Save case
        case_manager.save_case(case_path)
        
        # Verify metadata file
        metadata_file = Path(case_path) / '.metadata.json'
        self.assertTrue(metadata_file.exists())


class TestSolverRegistry(unittest.TestCase):
    """Test solver registry"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = SolverRegistry()
    
    def test_get_solver_list(self):
        """Test getting solver list"""
        solvers = self.registry.get_solver_list()
        self.assertIsInstance(solvers, list)
        self.assertIn('simpleFoam', solvers)
        self.assertIn('pimpleFoam', solvers)
        self.assertIn('interFoam', solvers)
    
    def test_get_solver_info(self):
        """Test getting solver information"""
        info = self.registry.get_solver_info('simpleFoam')
        self.assertIsInstance(info, dict)
        self.assertIn('description', info)
        self.assertIn('required_fields', info)
        self.assertIn('turbulence_models', info)
    
    def test_validate_solver_setup_valid(self):
        """Test valid solver setup validation"""
        fields = ['U', 'p', 'k', 'epsilon']
        is_valid, missing = self.registry.validate_solver_setup('simpleFoam', fields)
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
    
    def test_validate_solver_setup_invalid(self):
        """Test invalid solver setup validation"""
        fields = ['U']  # Missing 'p'
        is_valid, missing = self.registry.validate_solver_setup('simpleFoam', fields)
        self.assertFalse(is_valid)
        self.assertIn('p', missing)
    
    def test_validate_unknown_solver(self):
        """Test validation with unknown solver"""
        fields = ['U', 'p']
        is_valid, missing = self.registry.validate_solver_setup('unknownSolver', fields)
        self.assertFalse(is_valid)


class TestBlockMeshGeneration(unittest.TestCase):
    """Test blockMesh dictionary generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_simple_block(self):
        """Test simple block generation"""
        # This would test the blockMesh editor's dictionary generation
        # For now, just verify the structure exists
        vertices = [
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ]
        
        block = {
            'vertices': list(range(8)),
            'cells': [10, 10, 10],
            'grading': [1, 1, 1]
        }
        
        self.assertEqual(len(vertices), 8)
        self.assertEqual(len(block['cells']), 3)


class TestResidualParsing(unittest.TestCase):
    """Test residual log parsing"""
    
    def test_parse_simple_residual(self):
        """Test parsing simple residual line"""
        log_line = "smoothSolver:  Solving for Ux, Initial residual = 0.999, Final residual = 0.001, No Iterations 10"
        
        import re
        match = re.search(r'Solving for (\w+),.*Initial residual = ([\d.e+-]+)', log_line)
        
        self.assertIsNotNone(match)
        field = match.group(1)
        residual = float(match.group(2))
        
        self.assertEqual(field, 'Ux')
        self.assertAlmostEqual(residual, 0.999, places=3)
    
    def test_parse_time_step(self):
        """Test parsing time step"""
        log_line = "Time = 100"
        
        import re
        match = re.search(r'Time\s*=\s*(\d+\.?\d*)', log_line)
        
        self.assertIsNotNone(match)
        time = float(match.group(1))
        self.assertEqual(time, 100)


def run_unit_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAppConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSolverRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockMeshGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestResidualParsing))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_unit_tests()
    sys.exit(0 if success else 1)
