import pytest
import os
from caffa_engine import CaffaCase
from main_gui import CaffaGUI

# --- Unit Tests for Engine ---

def test_engine_defaults():
    case = CaffaCase()
    # Check default physics from caffa.f INIT
    assert case.physics['DENS'] == 1.0
    assert case.physics['VISC'] == 0.001
    assert case.logical_control['LTIME'] is False

def test_model_switching():
    case = CaffaCase()
    # Default is laminar-ish (ITE, IED false)
    case.set_physics_model("Laminar")
    assert case.lcal[4] is False
    
    case.set_physics_model("k-omega")
    assert case.lcal[4] is True # ITE
    assert case.lcal[5] is True # IED

def test_cin_file_generation(tmp_path):
    case = CaffaCase()
    case.title = "TEST_CASE"
    case.physics['DENS'] = 999.0
    
    file_path = tmp_path / "test.cin"
    case.write_cin_file(str(file_path))
    
    assert file_path.exists()
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Check Title (Record 1)
    assert "TEST_CASE" in lines[0]
    # Check Density (Record 5)
    assert "999.0" in lines[4] 

# --- GUI Functional Tests ---

def test_gui_startup(qtbot):
    window = CaffaGUI()
    qtbot.addWidget(window)
    assert window.windowTitle() == "PyCAFFA - CFD Solver Interface"

def test_gui_physics_update(qtbot):
    window = CaffaGUI()
    qtbot.addWidget(window)
    
    # Select Physics Node
    window.show_physics_ui()
    
    # Ensure update reflects in engine
    # (Simulating user interaction is complex, verifying direct linkage here)
    window.case.set_physics_model("k-omega")
    assert window.case.lcal[4] is True

def test_run_simulation_mock(qtbot):
    window = CaffaGUI()
    qtbot.addWidget(window)
    
    # Run the mock solver
    window.run_solver()
    
    # Check if plotting occurred (actors added to renderer)
    assert len(window.plotter.renderer.actors) > 0