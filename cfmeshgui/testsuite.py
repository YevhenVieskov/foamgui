import unittest
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

# Import classes from the main file (Assuming main file is named 'main.py')
# If running in same file, these imports are not needed.
from main import MeshDictValidator, OpenFoamGUI

# Ensure one QApplication exists
app = QApplication([])

class TestMeshDictValidator(unittest.TestCase):
    """Unit Tests for Logic"""

    def test_valid_config(self):
        config = {
            "maxCellSize": 1.0,
            "boundaryLayers": {"nLayers": 3},
            "surfaceFile": "geom.stl"
        }
        is_valid, errors = MeshDictValidator.validate(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_cell_size(self):
        config = {"maxCellSize": -5.0}
        is_valid, errors = MeshDictValidator.validate(config)
        self.assertFalse(is_valid)
        self.assertIn("maxCellSize must be a positive number.", errors)

    def test_invalid_file_extension(self):
        config = {
            "maxCellSize": 1.0,
            "surfaceFile": "geom.txt"
        }
        is_valid, errors = MeshDictValidator.validate(config)
        self.assertFalse(is_valid)
        self.assertIn("surfaceFile must be an STL or FMS file.", errors)


class TestGUIFunctional(unittest.TestCase):
    """Functional Tests for GUI interactions"""

    def setUp(self):
        self.gui = OpenFoamGUI()

    def test_tree_populates_table(self):
        """Test that clicking a tree node populates the table correctly (Parser logic)."""
        
        # Simulate selecting "Global Settings"
        # We know "Global Settings" is at index 0 based on populate_tree order
        tree_item = self.gui.tree.topLevelItem(0)
        self.assertEqual(tree_item.text(0), "Global Settings")
        
        # Manually trigger the slot (Simulating a click)
        self.gui.tree.setCurrentItem(tree_item)
        self.gui.on_tree_click(tree_item, 0)
        
        # Check Table Content
        # We expect "maxCellSize" to be in the table
        found_key = False
        for row in range(self.gui.table.rowCount()):
            key_item = self.gui.table.item(row, 0)
            if key_item.text() == "maxCellSize":
                found_key = True
                val_item = self.gui.table.item(row, 1)
                self.assertEqual(val_item.text(), "1.0")
                break
        
        self.assertTrue(found_key, "Table did not populate maxCellSize from Global Settings")

    def test_table_updates_data(self):
        """Test that editing the table updates the internal mesh_data dictionary."""
        
        # 1. Select Global Settings
        tree_item = self.gui.tree.topLevelItem(0)
        self.gui.tree.setCurrentItem(tree_item)
        self.gui.on_tree_click(tree_item, 0)
        
        # 2. Find row for maxCellSize
        target_row = -1
        for row in range(self.gui.table.rowCount()):
            if self.gui.table.item(row, 0).text() == "maxCellSize":
                target_row = row
                break
        
        # 3. Edit the Value (Simulate user typing "5.5")
        item_to_edit = self.gui.table.item(target_row, 1)
        item_to_edit.setText("5.5")
        
        # Trigger the change signal manually
        self.gui.on_table_edit(item_to_edit)
        
        # 4. Check Internal Data
        new_val = self.gui.mesh_data["Global Settings"]["maxCellSize"]
        self.assertEqual(new_val, 5.5)

    def test_clipping_logic(self):
        """Test that toggling clipping changes the state."""
        self.gui.load_geometry() # specific to load the mesh first
        
        # Initial state
        self.assertFalse(self.gui.clip_active)
        
        # Toggle On
        self.gui.toggle_clipping()
        self.assertTrue(self.gui.clip_active)
        
        # Toggle Off
        self.gui.toggle_clipping()
        self.assertFalse(self.gui.clip_active)

if __name__ == '__main__':
    unittest.main()