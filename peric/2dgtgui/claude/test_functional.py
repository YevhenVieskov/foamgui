"""
Functional Tests for CAFFA GUI
Tests the complete workflow and user interactions
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from caffa_reader import create_sample_data, CAFFAReader


class TestMatplotlibViewerFunctional(unittest.TestCase):
    """Functional tests for matplotlib-based viewer"""
    
    def setUp(self):
        """Set up test environment"""
        self.sample_data = create_sample_data(20, 15)
        self.reader = CAFFAReader()
        self.reader.data = self.sample_data
    
    def test_data_loading_workflow(self):
        """Test complete data loading workflow"""
        # Create sample data
        data = create_sample_data(30, 25)
        
        # Verify data is complete
        self.assertIsNotNone(data)
        self.assertEqual(data.grid.ni, 30)
        self.assertEqual(data.grid.nj, 25)
        
        # Verify all fields are available
        self.assertEqual(len(data.u), 30 * 25)
        self.assertEqual(len(data.v), 30 * 25)
        self.assertEqual(len(data.p), 30 * 25)
        self.assertEqual(len(data.t), 30 * 25)
    
    def test_field_extraction_workflow(self):
        """Test workflow for extracting different fields"""
        fields = ['u', 'v', 'p', 't', 'te', 'vmag']
        
        for field in fields:
            field_data = self.reader.get_cell_centered_data(field)
            self.assertEqual(field_data.shape, (15, 20))
            self.assertTrue(np.all(np.isfinite(field_data)))
    
    def test_coordinate_extraction_workflow(self):
        """Test coordinate extraction for plotting"""
        x, y = self.reader.get_coordinates()
        
        self.assertEqual(x.shape, (15, 20))
        self.assertEqual(y.shape, (15, 20))
        self.assertTrue(np.all(np.isfinite(x)))
        self.assertTrue(np.all(np.isfinite(y)))
    
    def test_statistics_calculation_workflow(self):
        """Test statistics calculation workflow"""
        field_data = self.reader.get_cell_centered_data('vmag')
        
        # Calculate statistics
        min_val = np.min(field_data)
        max_val = np.max(field_data)
        mean_val = np.mean(field_data)
        std_val = np.std(field_data)
        
        # Verify statistics are reasonable
        self.assertTrue(min_val >= 0)  # Velocity magnitude should be positive
        self.assertTrue(max_val > min_val)
        self.assertTrue(min_val <= mean_val <= max_val)
        self.assertTrue(std_val >= 0)
    
    def test_multiple_field_visualization_workflow(self):
        """Test visualizing multiple fields in sequence"""
        fields = ['u', 'v', 'p', 't']
        
        x, y = self.reader.get_coordinates()
        
        for field in fields:
            data = self.reader.get_cell_centered_data(field)
            
            # Simulate contour plot creation
            self.assertEqual(data.shape, x.shape)
            self.assertEqual(data.shape, y.shape)
            
            # Verify data is plottable
            self.assertTrue(np.all(np.isfinite(data)))
    
    def test_vector_field_workflow(self):
        """Test vector field extraction and preparation"""
        u = self.reader.get_cell_centered_data('u')
        v = self.reader.get_cell_centered_data('v')
        x, y = self.reader.get_coordinates()
        
        # Simulate subsampling for vector plot
        step = 2
        u_sub = u[::step, ::step]
        v_sub = v[::step, ::step]
        x_sub = x[::step, ::step]
        y_sub = y[::step, ::step]
        
        # Verify subsampled data is correct
        self.assertEqual(u_sub.shape, x_sub.shape)
        self.assertEqual(v_sub.shape, y_sub.shape)
    
    def test_streamline_data_workflow(self):
        """Test data preparation for streamlines"""
        u = self.reader.get_cell_centered_data('u')
        v = self.reader.get_cell_centered_data('v')
        x, y = self.reader.get_coordinates()
        
        # Verify data is suitable for streamline computation
        self.assertTrue(np.all(np.isfinite(u)))
        self.assertTrue(np.all(np.isfinite(v)))
        self.assertEqual(u.shape, x.shape)
        self.assertEqual(v.shape, y.shape)


class TestVisualizationWorkflows(unittest.TestCase):
    """Test complete visualization workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.data = create_sample_data(30, 20)
        self.reader = CAFFAReader()
        self.reader.data = self.data
    
    def test_contour_visualization_workflow(self):
        """Test complete contour visualization workflow"""
        # Get data
        x, y = self.reader.get_coordinates()
        field = self.reader.get_cell_centered_data('vmag')
        
        # Prepare contour levels
        num_levels = 20
        levels = np.linspace(np.min(field), np.max(field), num_levels)
        
        # Verify contour data is ready
        self.assertEqual(len(levels), num_levels)
        self.assertTrue(levels[0] <= levels[-1])
    
    def test_mesh_visualization_workflow(self):
        """Test mesh visualization workflow"""
        x, y = self.reader.get_coordinates()
        
        # Simulate mesh line extraction
        # Horizontal lines
        for j in range(y.shape[0]):
            x_line = x[j, :]
            y_line = y[j, :]
            self.assertEqual(len(x_line), self.data.grid.ni)
        
        # Vertical lines
        for i in range(x.shape[1]):
            x_line = x[:, i]
            y_line = y[:, i]
            self.assertEqual(len(x_line), self.data.grid.nj)
    
    def test_combined_visualization_workflow(self):
        """Test combined visualization (contours + vectors + mesh)"""
        # Get all required data
        x, y = self.reader.get_coordinates()
        u = self.reader.get_cell_centered_data('u')
        v = self.reader.get_cell_centered_data('v')
        vmag = self.reader.get_cell_centered_data('vmag')
        
        # Verify all data is consistent
        self.assertEqual(x.shape, y.shape)
        self.assertEqual(u.shape, v.shape)
        self.assertEqual(vmag.shape, x.shape)
        
        # Verify all data is finite
        self.assertTrue(np.all(np.isfinite(x)))
        self.assertTrue(np.all(np.isfinite(y)))
        self.assertTrue(np.all(np.isfinite(u)))
        self.assertTrue(np.all(np.isfinite(v)))
        self.assertTrue(np.all(np.isfinite(vmag)))


class TestDataProcessingWorkflows(unittest.TestCase):
    """Test data processing workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.data = create_sample_data(40, 30)
        self.reader = CAFFAReader()
        self.reader.data = self.data
    
    def test_field_calculation_workflow(self):
        """Test custom field calculation workflow"""
        # Get base fields
        u = self.reader.get_cell_centered_data('u')
        v = self.reader.get_cell_centered_data('v')
        
        # Calculate derived quantities
        vmag = np.sqrt(u**2 + v**2)
        kinetic_energy = 0.5 * (u**2 + v**2)
        
        # Verify calculations
        self.assertEqual(vmag.shape, u.shape)
        self.assertEqual(kinetic_energy.shape, u.shape)
        self.assertTrue(np.all(vmag >= 0))
        self.assertTrue(np.all(kinetic_energy >= 0))


def run_functional_tests():
    """Run all functional tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMatplotlibViewerFunctional))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessingWorkflows))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_functional_tests()
    exit(0 if success else 1)
