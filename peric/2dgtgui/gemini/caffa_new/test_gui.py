import sys
import unittest
import numpy as np
from qtpy import QtWidgets
from star_caffa_gui import CAFFADataParser, StarCaffaWindow, ResidualPlotter

app = QtWidgets.QApplication(sys.argv)

class TestCAFFAGUI(unittest.TestCase):
    
    def test_data_parser_grid(self):
        """Unit test: Ensure the data parser generates a valid PyVista grid with CAFFA fields."""
        grid = CAFFADataParser.read_mesh_and_fields()
        self.assertIsNotNone(grid)
        self.assertIn("Velocity", grid.array_names)
        self.assertIn("Pressure", grid.array_names)
        
        # Check if arrays have correct shapes 
        self.assertEqual(grid["Velocity"].shape[1], 3) # 3D vector for PyVista

    def test_data_parser_residuals(self):
        """Unit test: Ensure residuals arrays are extracted correctly."""
        iters, u, p = CAFFADataParser.read_residuals()
        self.assertEqual(len(iters), len(u))
        self.assertEqual(len(iters), len(p))
        self.assertTrue(np.all(u > 0)) # Residuals should be positive for log scale

    def test_gui_initialization(self):
        """Functional test: Ensure the main window builds the Tree and PyVista components."""
        window = StarCaffaWindow()
        self.assertIsNotNone(window.tree)
        self.assertIsNotNone(window.plotter)
        self.assertIsNotNone(window.residuals_widget)
        
        # Check if scenes are populated
        items = window.tree.findItems("Scenes", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[0].childCount(), 3)

    def test_residual_plot_update(self):
        """Functional test: Test if the matplotlib canvas updates without throwing errors."""
        plotter = ResidualPlotter()
        iters, u, p = CAFFADataParser.read_residuals()
        try:
            plotter.update_plot(iters, u, p)
            success = True
        except Exception as e:
            success = False
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()