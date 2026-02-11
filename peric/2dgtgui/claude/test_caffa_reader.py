"""
Unit Tests for CAFFA Reader and GUI Components
"""
import unittest
import numpy as np
import tempfile
import os
import struct
from caffa_reader import (
    CAFFAReader, CAFFAData, CAFFAGrid,
    create_sample_data
)


class TestCAFFAGrid(unittest.TestCase):
    """Test CAFFAGrid dataclass"""
    
    def test_grid_creation(self):
        """Test creating a grid object"""
        ni, nj = 10, 8
        nij = ni * nj
        x = np.linspace(0, 1, nij)
        y = np.linspace(0, 1, nij)
        
        grid = CAFFAGrid(
            ni=ni, nj=nj, nim=ni-1, njm=nj-1, nij=nij,
            x=x, y=y, xc=x, yc=y
        )
        
        self.assertEqual(grid.ni, ni)
        self.assertEqual(grid.nj, nj)
        self.assertEqual(grid.nij, nij)
        self.assertEqual(len(grid.x), nij)
        self.assertEqual(len(grid.y), nij)


class TestCAFFAData(unittest.TestCase):
    """Test CAFFAData dataclass"""
    
    def setUp(self):
        """Set up test data"""
        self.data = create_sample_data(20, 15)
    
    def test_data_creation(self):
        """Test creating data object"""
        self.assertIsInstance(self.data, CAFFAData)
        self.assertEqual(self.data.grid.ni, 20)
        self.assertEqual(self.data.grid.nj, 15)
        self.assertEqual(self.data.grid.nij, 300)
    
    def test_velocity_magnitude(self):
        """Test velocity magnitude calculation"""
        vmag = self.data.velocity_magnitude
        
        # Check shape
        self.assertEqual(vmag.shape, self.data.u.shape)
        
        # Check values are non-negative
        self.assertTrue(np.all(vmag >= 0))
        
        # Check calculation is correct
        expected = np.sqrt(self.data.u**2 + self.data.v**2)
        np.testing.assert_array_almost_equal(vmag, expected)
    
    def test_vorticity(self):
        """Test vorticity calculation"""
        vort = self.data.vorticity
        self.assertEqual(vort.shape, self.data.u.shape)


class TestCAFFAReader(unittest.TestCase):
    """Test CAFFA file reader"""
    
    def setUp(self):
        """Set up test reader"""
        self.reader = CAFFAReader()
    
    def test_reader_initialization(self):
        """Test reader initialization"""
        self.assertIsNone(self.reader.data)
    
    def test_create_sample_data(self):
        """Test sample data creation"""
        ni, nj = 25, 20
        data = create_sample_data(ni, nj)
        
        self.assertEqual(data.grid.ni, ni)
        self.assertEqual(data.grid.nj, nj)
        self.assertEqual(data.grid.nij, ni * nj)
        
        # Check all fields have correct size
        self.assertEqual(len(data.u), ni * nj)
        self.assertEqual(len(data.v), ni * nj)
        self.assertEqual(len(data.p), ni * nj)
        self.assertEqual(len(data.t), ni * nj)
        self.assertEqual(len(data.te), ni * nj)
        self.assertEqual(len(data.dissipation), ni * nj)
    
    def test_write_and_read_binary(self):
        """Test writing and reading binary file"""
        # Create sample data
        original_data = create_sample_data(10, 8)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pos') as f:
            temp_filename = f.name
            
            # Write data in Fortran unformatted format
            nij = original_data.grid.nij
            
            # Calculate record size
            header_size = 7 * 4  # 7 integers
            coord_size = 4 * nij * 4  # 4 float arrays (x, y, xc, yc)
            field_size = 8 * nij * 4  # 8 float arrays
            rec_size = header_size + coord_size + field_size
            
            # Write record marker
            f.write(struct.pack('i', rec_size))
            
            # Write header
            f.write(struct.pack('i', original_data.itim))
            f.write(struct.pack('f', original_data.time))
            f.write(struct.pack('i', original_data.grid.ni))
            f.write(struct.pack('i', original_data.grid.nj))
            f.write(struct.pack('i', original_data.grid.nim))
            f.write(struct.pack('i', original_data.grid.njm))
            f.write(struct.pack('i', original_data.grid.nij))
            
            # Write coordinates
            f.write(struct.pack(f'{nij}f', *original_data.grid.x))
            f.write(struct.pack(f'{nij}f', *original_data.grid.y))
            f.write(struct.pack(f'{nij}f', *original_data.grid.xc))
            f.write(struct.pack(f'{nij}f', *original_data.grid.yc))
            
            # Write flow fields
            f.write(struct.pack(f'{nij}f', *original_data.f1))
            f.write(struct.pack(f'{nij}f', *original_data.f2))
            f.write(struct.pack(f'{nij}f', *original_data.u))
            f.write(struct.pack(f'{nij}f', *original_data.v))
            f.write(struct.pack(f'{nij}f', *original_data.p))
            f.write(struct.pack(f'{nij}f', *original_data.t))
            f.write(struct.pack(f'{nij}f', *original_data.te))
            f.write(struct.pack(f'{nij}f', *original_data.dissipation))
            
            # Write end marker
            f.write(struct.pack('i', rec_size))
        
        try:
            # Read back the data
            read_data = self.reader.read_binary_file(temp_filename)
            
            # Verify
            self.assertEqual(read_data.itim, original_data.itim)
            self.assertAlmostEqual(read_data.time, original_data.time, places=5)
            self.assertEqual(read_data.grid.ni, original_data.grid.ni)
            self.assertEqual(read_data.grid.nj, original_data.grid.nj)
            
            np.testing.assert_array_almost_equal(read_data.u, original_data.u)
            np.testing.assert_array_almost_equal(read_data.v, original_data.v)
            np.testing.assert_array_almost_equal(read_data.p, original_data.p)
            
        finally:
            # Clean up
            os.unlink(temp_filename)
    
    def test_get_cell_centered_data(self):
        """Test getting cell-centered data"""
        data = create_sample_data(20, 15)
        self.reader.data = data
        
        # Test valid fields
        for field in ['u', 'v', 'p', 't', 'te', 'vmag']:
            field_data = self.reader.get_cell_centered_data(field)
            self.assertEqual(field_data.shape, (15, 20))
        
        # Test invalid field
        with self.assertRaises(ValueError):
            self.reader.get_cell_centered_data('invalid_field')
    
    def test_get_cell_centered_data_no_data(self):
        """Test error when no data loaded"""
        with self.assertRaises(ValueError):
            self.reader.get_cell_centered_data('u')
    
    def test_get_coordinates(self):
        """Test getting coordinates"""
        data = create_sample_data(20, 15)
        self.reader.data = data
        
        x, y = self.reader.get_coordinates()
        
        self.assertEqual(x.shape, (15, 20))
        self.assertEqual(y.shape, (15, 20))
    
    def test_get_coordinates_no_data(self):
        """Test error when getting coordinates with no data"""
        with self.assertRaises(ValueError):
            self.reader.get_coordinates()


class TestSampleDataGeneration(unittest.TestCase):
    """Test sample data generation"""
    
    def test_sample_data_properties(self):
        """Test properties of generated sample data"""
        ni, nj = 30, 25
        data = create_sample_data(ni, nj)
        
        # Check grid dimensions
        self.assertEqual(data.grid.ni, ni)
        self.assertEqual(data.grid.nj, nj)
        self.assertEqual(data.grid.nij, ni * nj)
        
        # Check time values
        self.assertEqual(data.itim, 1)
        self.assertEqual(data.time, 1.0)
        
        # Check field ranges are reasonable
        self.assertTrue(np.all(np.abs(data.u) <= 2.0))
        self.assertTrue(np.all(np.abs(data.v) <= 2.0))
        self.assertTrue(np.all(data.te >= 0))
        self.assertTrue(np.all(data.dissipation >= 0))
    
    def test_sample_data_coordinates(self):
        """Test coordinate generation"""
        ni, nj = 40, 30
        data = create_sample_data(ni, nj)
        
        # Check coordinate ranges
        self.assertTrue(np.min(data.grid.xc) >= 0)
        self.assertTrue(np.max(data.grid.xc) <= 1)
        self.assertTrue(np.min(data.grid.yc) >= 0)
        self.assertTrue(np.max(data.grid.yc) <= 1)
    
    def test_different_grid_sizes(self):
        """Test creating sample data with different grid sizes"""
        test_cases = [
            (10, 10),
            (50, 30),
            (100, 50),
            (5, 5),
        ]
        
        for ni, nj in test_cases:
            data = create_sample_data(ni, nj)
            self.assertEqual(data.grid.ni, ni)
            self.assertEqual(data.grid.nj, nj)
            self.assertEqual(len(data.u), ni * nj)


class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def test_empty_grid(self):
        """Test handling of minimal grid"""
        data = create_sample_data(2, 2)
        self.assertEqual(data.grid.nij, 4)
    
    def test_rectangular_grids(self):
        """Test non-square grids"""
        data1 = create_sample_data(50, 10)
        data2 = create_sample_data(10, 50)
        
        self.assertEqual(data1.grid.nij, 500)
        self.assertEqual(data2.grid.nij, 500)
        self.assertNotEqual(data1.grid.ni, data1.grid.nj)
        self.assertNotEqual(data2.grid.ni, data2.grid.nj)
    
    def test_velocity_divergence(self):
        """Test that generated velocity field properties"""
        data = create_sample_data(30, 30)
        
        # Reshape to 2D
        u_2d = data.u.reshape(30, 30)
        v_2d = data.v.reshape(30, 30)
        
        # Check that velocities are reasonable
        self.assertTrue(np.all(np.isfinite(u_2d)))
        self.assertTrue(np.all(np.isfinite(v_2d)))


class TestNumericalAccuracy(unittest.TestCase):
    """Test numerical accuracy of calculations"""
    
    def test_velocity_magnitude_accuracy(self):
        """Test accuracy of velocity magnitude calculation"""
        data = create_sample_data(20, 20)
        
        # Manual calculation
        vmag_manual = np.sqrt(data.u**2 + data.v**2)
        vmag_method = data.velocity_magnitude
        
        # Should be identical
        np.testing.assert_array_almost_equal(vmag_manual, vmag_method, decimal=10)
    
    def test_coordinate_reshape(self):
        """Test coordinate reshaping accuracy"""
        ni, nj = 25, 30
        data = create_sample_data(ni, nj)
        reader = CAFFAReader()
        reader.data = data
        
        x, y = reader.get_coordinates()
        
        # Check shapes
        self.assertEqual(x.shape, (nj, ni))
        self.assertEqual(y.shape, (nj, ni))
        
        # Check values preserved
        x_flat = x.flatten()
        y_flat = y.flatten()
        np.testing.assert_array_almost_equal(x_flat, data.grid.xc)
        np.testing.assert_array_almost_equal(y_flat, data.grid.yc)


def run_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCAFFAGrid))
    suite.addTests(loader.loadTestsFromTestCase(TestCAFFAData))
    suite.addTests(loader.loadTestsFromTestCase(TestCAFFAReader))
    suite.addTests(loader.loadTestsFromTestCase(TestSampleDataGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestNumericalAccuracy))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
