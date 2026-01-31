import pytest
import numpy as np
from PyQt6.QtCore import Qt
from grid_engine import GridEngine
from main_gui import StarCCMGridGUI

# --- Unit Tests for Engine ---

def test_engine_initialization():
    """Test default values of GridEngine."""
    engine = GridEngine()
    assert engine.nicv == 10
    assert engine.njcv == 10
    assert engine.ngr == 1

def test_set_params():
    [cite_start]"""Test setting parameters[cite: 46]."""
    engine = GridEngine()
    engine.set_control_params(ngr=3, idir=1, nicv=50, njcv=20)
    assert engine.ngr == 3
    assert engine.idir == 1
    assert engine.nicv == 50
    assert engine.ni == 52  # NICV + 2

def test_grid_generation_shape():
    """Test if generate_grid produces arrays of correct shape."""
    engine = GridEngine()
    engine.set_control_params(1, 0, 10, 10) # NI=12, NJ=12
    xx, yy, zz = engine.generate_grid()
    
    expected_shape = (12, 12)
    assert xx.shape == expected_shape
    assert yy.shape == expected_shape
    assert zz.shape == expected_shape

# --- Functional/GUI Tests ---

def test_gui_title(qtbot):
    """Test window title initialization."""
    window = StarCCMGridGUI()
    qtbot.addWidget(window)
    assert "Star-CCM+" in window.windowTitle() or "PyCAFFA" in window.windowTitle()

def test_parameter_update_from_gui(qtbot):
    """Test that changing GUI spinners updates the engine."""
    window = StarCCMGridGUI()
    qtbot.addWidget(window)
    
    # Simulate clicking "Parameters" in tree
    # (In a real test, we might programmatically select the tree item, 
    # here we assume the method shows the UI correctly)
    window.show_parameters_ui()
    
    # Change values
    window.spin_nicv.setValue(25)
    window.spin_njcv.setValue(30)
    
    # Click Apply
    # Find the apply button in the layout or invoke method directly
    window.apply_parameters()
    
    assert window.engine.nicv == 25
    assert window.engine.njcv == 30

def test_generate_mesh_action(qtbot):
    """Test the generate mesh integration."""
    window = StarCCMGridGUI()
    qtbot.addWidget(window)
    
    # Setup simple params
    window.engine.set_control_params(1, 0, 5, 5)
    
    # Run generation
    window.generate_mesh()
    
    # Check if actor was added to plotter
    assert window.mesh_actor is not None