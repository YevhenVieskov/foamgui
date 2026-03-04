"""
Unit Tests for CFD Data Loader
"""

import pytest
import numpy as np
import tempfile
import os
from gui.data_loader import CFDDataLoader

class TestCFDDataLoader:
    """Test cases for CFDDataLoader"""
    
    @pytest.fixture
    def loader(self):
        """Create loader instance"""
        return CFDDataLoader()
    
    @pytest.fixture
    def sample_csv_file(self):
        """Create sample CSV file for testing"""
        content = """iteration,continuity,x_velocity,y_velocity,z_velocity
0,1e-3,1e-3,1e-3,1e-3
1,5e-4,5e-4,5e-4,5e-4
2,1e-4,1e-4,1e-4,1e-4
3,5e-5,5e-5,5e-5,5e-5
4,1e-5,1e-5,1e-5,1e-5
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            return f.name
    
    def test_load_csv(self, loader, sample_csv_file):
        """Test loading CSV file"""
        data = loader.load(sample_csv_file)
        
        assert 'mesh' in data
        assert 'residuals' in data
        assert len(data['residuals']) == 5
        assert data['residuals'][0]['iteration'] == 0
    
    def test_load_nonexistent_file(self, loader):
        """Test loading nonexistent file"""
        with pytest.raises(FileNotFoundError):
            loader.load('/nonexistent/file.csv')
    
    def test_generate_sample_residuals(self, loader):
        """Test sample residual generation"""
        residuals = loader._generate_sample_residuals(n_iterations=50)
        
        assert len(residuals) == 50
        assert 'continuity' in residuals[0]
        assert 'iteration' in residuals[0]
        
        # Check convergence trend
        assert residuals[0]['continuity'] > residuals[-1]['continuity']
    
    def test_create_sample_mesh(self, loader):
        """Test sample mesh creation"""
        mesh = loader._create_sample_mesh()
        
        assert mesh is not None
        assert 'pressure' in mesh.point_data
        assert 'velocity' in mesh.point_data
        assert len(mesh.points) > 0
    
    def teardown_method(self, method):
        """Cleanup after each test"""
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
