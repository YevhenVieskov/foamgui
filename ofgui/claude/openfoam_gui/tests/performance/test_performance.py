"""
Performance tests for OpenFOAM GUI
"""
import pytest
import time
import sys
import tempfile
import shutil
from pathlib import Path
import psutil
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.config import AppConfig
from core.case_manager import CaseManager
from solvers.solver_registry_extended import ExtendedSolverRegistry
from utils.mesh_quality import MeshQualityChecker


class PerformanceMetrics:
    """Track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.process = psutil.Process()
    
    def start(self, test_name: str):
        """Start timing a test"""
        self.metrics[test_name] = {
            'start_time': time.time(),
            'start_memory': self.process.memory_info().rss / 1024 / 1024,  # MB
            'start_cpu': self.process.cpu_percent()
        }
    
    def end(self, test_name: str):
        """End timing a test"""
        if test_name in self.metrics:
            self.metrics[test_name]['end_time'] = time.time()
            self.metrics[test_name]['end_memory'] = self.process.memory_info().rss / 1024 / 1024
            self.metrics[test_name]['end_cpu'] = self.process.cpu_percent()
            
            # Calculate deltas
            self.metrics[test_name]['duration'] = (
                self.metrics[test_name]['end_time'] - 
                self.metrics[test_name]['start_time']
            )
            self.metrics[test_name]['memory_delta'] = (
                self.metrics[test_name]['end_memory'] - 
                self.metrics[test_name]['start_memory']
            )
    
    def report(self):
        """Generate performance report"""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        
        for test_name, metrics in self.metrics.items():
            print(f"\n{test_name}:")
            print(f"  Duration:       {metrics.get('duration', 0):.3f} seconds")
            print(f"  Memory Delta:   {metrics.get('memory_delta', 0):.2f} MB")
            print(f"  CPU Usage:      {metrics.get('end_cpu', 0):.1f}%")
        
        print("\n" + "="*60)


@pytest.fixture
def perf_metrics():
    """Fixture for performance metrics"""
    return PerformanceMetrics()


@pytest.fixture
def temp_case_dir():
    """Create temporary case directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestConfigPerformance:
    """Performance tests for configuration system"""
    
    def test_config_load_performance(self, perf_metrics, tmp_path):
        """Test configuration loading performance"""
        config_file = tmp_path / 'perf_config.json'
        
        perf_metrics.start('config_load')
        
        # Load configuration 100 times
        for i in range(100):
            config = AppConfig(str(config_file))
            config.set(f'key_{i}', f'value_{i}')
        
        perf_metrics.end('config_load')
        
        # Should complete in reasonable time
        assert perf_metrics.metrics['config_load']['duration'] < 5.0
    
    def test_config_save_performance(self, perf_metrics, tmp_path):
        """Test configuration save performance"""
        config_file = tmp_path / 'perf_config.json'
        config = AppConfig(str(config_file))
        
        perf_metrics.start('config_save')
        
        # Save configuration 100 times
        for i in range(100):
            config.set(f'key_{i}', f'value_{i}')
            config.save()
        
        perf_metrics.end('config_save')
        
        # Should complete in reasonable time
        assert perf_metrics.metrics['config_save']['duration'] < 10.0
    
    def test_config_memory_usage(self, perf_metrics, tmp_path):
        """Test configuration memory usage"""
        config_file = tmp_path / 'perf_config.json'
        
        perf_metrics.start('config_memory')
        
        configs = []
        for i in range(100):
            config = AppConfig(str(config_file))
            configs.append(config)
        
        perf_metrics.end('config_memory')
        
        # Memory delta should be reasonable
        memory_delta = perf_metrics.metrics['config_memory']['memory_delta']
        print(f"Memory for 100 configs: {memory_delta:.2f} MB")
        assert memory_delta < 50  # Less than 50MB for 100 configs


class TestCaseManagerPerformance:
    """Performance tests for case manager"""
    
    def test_case_creation_performance(self, perf_metrics, tmp_path):
        """Test case creation performance"""
        config = AppConfig()
        manager = CaseManager(config)
        
        perf_metrics.start('case_creation')
        
        # Create 10 cases
        for i in range(10):
            case_data = {
                'name': f'perfCase_{i}',
                'path': str(tmp_path),
                'solver': 'simpleFoam',
                'dimension': '3D'
            }
            case_path = manager.create_case(case_data)
            assert case_path is not None
        
        perf_metrics.end('case_creation')
        
        # Should create 10 cases quickly
        assert perf_metrics.metrics['case_creation']['duration'] < 5.0
    
    def test_case_loading_performance(self, perf_metrics, tmp_path):
        """Test case loading performance"""
        config = AppConfig()
        manager = CaseManager(config)
        
        # Create a test case
        case_data = {
            'name': 'perfCase',
            'path': str(tmp_path),
            'solver': 'simpleFoam',
            'dimension': '3D'
        }
        case_path = manager.create_case(case_data)
        
        perf_metrics.start('case_loading')
        
        # Load case 100 times
        for i in range(100):
            manager.load_case(case_path)
        
        perf_metrics.end('case_loading')
        
        # Should load quickly
        assert perf_metrics.metrics['case_loading']['duration'] < 2.0
    
    def test_large_case_creation(self, perf_metrics, tmp_path):
        """Test creating case with many files"""
        config = AppConfig()
        manager = CaseManager(config)
        
        case_data = {
            'name': 'largeCase',
            'path': str(tmp_path),
            'solver': 'pimpleFoam',
            'dimension': '3D'
        }
        
        perf_metrics.start('large_case_creation')
        
        case_path = manager.create_case(case_data)
        
        # Create many time directories
        for i in range(50):
            time_dir = Path(case_path) / str(i)
            time_dir.mkdir()
            # Create field files
            for field in ['U', 'p', 'k', 'epsilon']:
                (time_dir / field).touch()
        
        perf_metrics.end('large_case_creation')
        
        duration = perf_metrics.metrics['large_case_creation']['duration']
        print(f"Large case creation: {duration:.3f}s")
        assert duration < 10.0


class TestSolverRegistryPerformance:
    """Performance tests for solver registry"""
    
    def test_registry_initialization(self, perf_metrics):
        """Test solver registry initialization"""
        perf_metrics.start('registry_init')
        
        for i in range(100):
            registry = ExtendedSolverRegistry()
        
        perf_metrics.end('registry_init')
        
        # Should initialize quickly
        assert perf_metrics.metrics['registry_init']['duration'] < 1.0
    
    def test_solver_lookup_performance(self, perf_metrics):
        """Test solver lookup performance"""
        registry = ExtendedSolverRegistry()
        
        perf_metrics.start('solver_lookup')
        
        # Lookup all solvers multiple times
        for _ in range(1000):
            for solver_name in registry.get_solver_list():
                info = registry.get_solver_info(solver_name)
        
        perf_metrics.end('solver_lookup')
        
        # Should be very fast
        assert perf_metrics.metrics['solver_lookup']['duration'] < 2.0
    
    def test_solver_validation_performance(self, perf_metrics):
        """Test solver validation performance"""
        registry = ExtendedSolverRegistry()
        
        perf_metrics.start('solver_validation')
        
        # Validate 1000 times
        for _ in range(1000):
            is_valid, missing = registry.validate_solver_setup('simpleFoam', ['U', 'p'])
        
        perf_metrics.end('solver_validation')
        
        # Should be very fast
        assert perf_metrics.metrics['solver_validation']['duration'] < 1.0
    
    def test_solver_search_performance(self, perf_metrics):
        """Test solver search performance"""
        registry = ExtendedSolverRegistry()
        
        search_terms = ['flow', 'heat', 'turbulent', 'incompressible', 'transient']
        
        perf_metrics.start('solver_search')
        
        for _ in range(100):
            for term in search_terms:
                results = registry.search_solvers(term)
        
        perf_metrics.end('solver_search')
        
        # Should search quickly
        assert perf_metrics.metrics['solver_search']['duration'] < 2.0


class TestMeshQualityPerformance:
    """Performance tests for mesh quality checking"""
    
    def test_quality_checker_initialization(self, perf_metrics, temp_case_dir):
        """Test mesh quality checker initialization"""
        perf_metrics.start('quality_init')
        
        for i in range(100):
            checker = MeshQualityChecker(temp_case_dir)
        
        perf_metrics.end('quality_init')
        
        assert perf_metrics.metrics['quality_init']['duration'] < 1.0
    
    def test_quality_assessment_performance(self, perf_metrics, temp_case_dir):
        """Test quality assessment performance"""
        checker = MeshQualityChecker(temp_case_dir)
        
        # Mock mesh stats
        checker.mesh_stats = {
            'cells': 10000,
            'faces': 30000,
            'points': 11000,
            'non_orthogonality': {'max': 45.5, 'average': 15.2},
            'skewness': {'max': 2.3, 'average': 0.8},
            'failed_checks': []
        }
        
        perf_metrics.start('quality_assessment')
        
        for _ in range(1000):
            assessment = checker.assess_quality()
        
        perf_metrics.end('quality_assessment')
        
        # Should assess quickly
        assert perf_metrics.metrics['quality_assessment']['duration'] < 2.0
    
    def test_quality_report_generation(self, perf_metrics, temp_case_dir):
        """Test quality report generation performance"""
        checker = MeshQualityChecker(temp_case_dir)
        
        checker.mesh_stats = {
            'cells': 10000,
            'faces': 30000,
            'points': 11000,
            'non_orthogonality': {'max': 45.5, 'average': 15.2},
            'skewness': {'max': 2.3, 'average': 0.8},
            'failed_checks': []
        }
        
        perf_metrics.start('report_generation')
        
        for _ in range(100):
            report = checker.generate_quality_report()
        
        perf_metrics.end('report_generation')
        
        assert perf_metrics.metrics['report_generation']['duration'] < 1.0


class TestMemoryLeaks:
    """Test for memory leaks"""
    
    def test_config_no_memory_leak(self, tmp_path):
        """Test configuration doesn't leak memory"""
        config_file = tmp_path / 'leak_test.json'
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Create and destroy many configs
        for i in range(1000):
            config = AppConfig(str(config_file))
            config.set('key', 'value')
            del config
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Should not leak significantly
        assert memory_increase < 20  # Less than 20MB increase
    
    def test_case_manager_no_memory_leak(self, tmp_path):
        """Test case manager doesn't leak memory"""
        config = AppConfig()
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Create and destroy many managers
        for i in range(100):
            manager = CaseManager(config)
            case_data = {
                'name': f'leakTest_{i}',
                'path': str(tmp_path),
                'solver': 'simpleFoam',
                'dimension': '3D'
            }
            case_path = manager.create_case(case_data)
            del manager
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Should not leak significantly
        assert memory_increase < 50


class TestScalability:
    """Test scalability with increasing data sizes"""
    
    def test_scaling_with_solver_count(self, perf_metrics):
        """Test performance scales with solver count"""
        registry = ExtendedSolverRegistry()
        
        results = []
        
        for multiplier in [1, 2, 5, 10]:
            perf_metrics.start(f'scale_{multiplier}')
            
            # Access all solvers multiple times
            for _ in range(multiplier * 100):
                for solver in registry.get_solver_list():
                    info = registry.get_solver_info(solver)
            
            perf_metrics.end(f'scale_{multiplier}')
            
            duration = perf_metrics.metrics[f'scale_{multiplier}']['duration']
            results.append((multiplier, duration))
            print(f"Multiplier {multiplier}: {duration:.3f}s")
        
        # Time should scale roughly linearly
        # Check that 10x work doesn't take more than 15x time
        if len(results) >= 2:
            ratio = results[-1][1] / results[0][1]
            assert ratio < 15
    
    def test_scaling_with_case_size(self, perf_metrics, tmp_path):
        """Test performance with increasing case complexity"""
        config = AppConfig()
        manager = CaseManager(config)
        
        for num_time_dirs in [10, 50, 100]:
            case_data = {
                'name': f'scaleCase_{num_time_dirs}',
                'path': str(tmp_path),
                'solver': 'pimpleFoam',
                'dimension': '3D'
            }
            
            perf_metrics.start(f'case_scale_{num_time_dirs}')
            
            case_path = manager.create_case(case_data)
            
            # Create time directories
            for i in range(num_time_dirs):
                time_dir = Path(case_path) / str(i * 0.1)
                time_dir.mkdir()
                for field in ['U', 'p']:
                    (time_dir / field).touch()
            
            perf_metrics.end(f'case_scale_{num_time_dirs}')
            
            duration = perf_metrics.metrics[f'case_scale_{num_time_dirs}']['duration']
            print(f"Time dirs {num_time_dirs}: {duration:.3f}s")


class TestConcurrency:
    """Test concurrent operations"""
    
    def test_concurrent_config_access(self, tmp_path):
        """Test concurrent configuration access"""
        import threading
        
        config_file = tmp_path / 'concurrent_config.json'
        config = AppConfig(str(config_file))
        
        def worker(worker_id):
            for i in range(100):
                config.set(f'worker_{worker_id}_key_{i}', f'value_{i}')
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Config should have data from all workers
        assert len(config.config) > 100


def run_performance_suite():
    """Run all performance tests with reporting"""
    perf_metrics = PerformanceMetrics()
    
    # Run tests
    pytest.main([__file__, '-v', '--tb=short', '-k', 'Performance'])
    
    # Print report
    perf_metrics.report()


if __name__ == '__main__':
    run_performance_suite()
