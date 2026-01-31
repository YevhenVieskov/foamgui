class TestSnappyValidator(unittest.TestCase):
    def test_valid_snappy_config(self):
        config = {
            "controls": {"castellatedMesh": True, "snap": True, "addLayers": False},
            "geometry": {"motor.stl": {"file": "motor.stl"}},
            "castellatedMeshControls": {
                "features": [{"level": 1}],
                "refinementSurfaces": {"motor.stl": {"level": [1, 2]}},
                "locationInMesh": [1, 1, 1]
            }
        }
        is_valid, errors = SnappyValidator.validate(config)
        self.assertTrue(is_valid)

    def test_inverted_levels(self):
        """Test if Min Level > Max Level is caught."""
        config = {
            "controls": {"castellatedMesh": True, "snap": True, "addLayers": False},
            "geometry": {"motor.stl": {"file": "motor.stl"}},
            "castellatedMeshControls": {
                "features": [],
                "refinementSurfaces": {"motor.stl": {"level": [5, 2]}}, # Error: 5 > 2
                "locationInMesh": [1, 1, 1]
            }
        }
        is_valid, errors = SnappyValidator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any("Min level" in e for e in errors))

    def test_missing_location(self):
        """Test if missing locationInMesh is caught."""
        config = {
            "controls": {"castellatedMesh": True, "snap": True, "addLayers": False},
            "geometry": {"motor.stl": {"file": "motor.stl"}},
            "castellatedMeshControls": {
                "features": [],
                "refinementSurfaces": {},
                "locationInMesh": [1, 1] # Error: needs 3 coords
            }
        }
        is_valid, errors = SnappyValidator.validate(config)
        self.assertFalse(is_valid)

class TestSnappyGenerator(unittest.TestCase):
    def test_file_generation(self):
        """Test if Python dict converts to OpenFOAM format string."""
        data = {
            "castellatedMesh": True,
            "snapControls": {"nSmoothPatch": 3}
        }
        lines = SnappyGenerator._dict_to_foam(data)
        
        # Check conversion
        self.assertIn("castellatedMesh on;", lines)
        # Check nesting
        self.assertIn("snapControls", lines)
        self.assertIn("    nSmoothPatch 3;", lines) # Check indentation