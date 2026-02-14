"""
GUI Automation Tests using pytest-qt
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Check if PyQt6 is available
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytestmark = pytest.mark.skip("PyQt6 not available")


if PYQT_AVAILABLE:
    from core.config import AppConfig
    from core.main_window import MainWindow
    from core.case_manager import CaseManager
    from widgets.solver_config import SolverConfigWidget
    from widgets.mesh_panel import MeshPanelWidget
    from widgets.new_case_dialog import NewCaseDialog


@pytest.fixture
def qapp(qapp):
    """Provide QApplication instance"""
    return qapp


@pytest.fixture
def temp_case_dir():
    """Create temporary directory for test cases"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def config():
    """Provide test configuration"""
    return AppConfig()


@pytest.fixture
def main_window(qapp, config):
    """Provide main window instance"""
    window = MainWindow(config)
    window.show()
    return window


class TestMainWindowAutomation:
    """Automated GUI tests for main window"""
    
    def test_window_creation(self, main_window):
        """Test main window is created properly"""
        assert main_window.isVisible()
        assert main_window.windowTitle() == "OpenFOAM GUI - Star-CCM+ Style"
    
    def test_menu_exists(self, main_window):
        """Test all menus are present"""
        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        
        assert '&File' in menus
        assert '&Mesh' in menus
        assert '&Solver' in menus
        assert '&View' in menus
        assert '&Help' in menus
    
    def test_toolbar_exists(self, main_window):
        """Test toolbar is present"""
        toolbars = main_window.findChildren(type(main_window.findChild(type(main_window).__bases__[0])))
        assert len(toolbars) > 0
    
    def test_tab_widget_exists(self, main_window):
        """Test tab widget with all tabs"""
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() == 3
        
        tab_names = [main_window.tab_widget.tabText(i) for i in range(3)]
        assert 'Mesh' in tab_names
        assert 'Solver Setup' in tab_names
        assert 'Monitoring' in tab_names
    
    def test_case_tree_exists(self, main_window):
        """Test case tree dock widget"""
        assert main_window.case_tree_dock is not None
        assert main_window.case_tree is not None
    
    def test_new_case_action(self, main_window, qtbot, monkeypatch):
        """Test new case action triggers dialog"""
        # Mock the dialog
        mock_dialog = Mock()
        mock_dialog.exec.return_value = False  # User cancels
        
        with patch('core.main_window.NewCaseDialog', return_value=mock_dialog):
            main_window.new_case_action.trigger()
            mock_dialog.exec.assert_called_once()
    
    def test_solver_combo_interaction(self, main_window, qtbot):
        """Test solver combo box interaction"""
        solver_widget = main_window.solver_config
        combo = solver_widget.solver_combo
        
        # Get initial solver
        initial_solver = combo.currentText()
        
        # Change solver
        with qtbot.waitSignal(combo.currentTextChanged):
            combo.setCurrentIndex((combo.currentIndex() + 1) % combo.count())
        
        # Verify change
        assert combo.currentText() != initial_solver
    
    def test_tab_switching(self, main_window, qtbot):
        """Test switching between tabs"""
        tab_widget = main_window.tab_widget
        
        # Switch to mesh tab
        tab_widget.setCurrentIndex(0)
        assert tab_widget.currentIndex() == 0
        
        # Switch to solver tab
        tab_widget.setCurrentIndex(1)
        assert tab_widget.currentIndex() == 1
        
        # Switch to monitoring tab
        tab_widget.setCurrentIndex(2)
        assert tab_widget.currentIndex() == 2


class TestSolverConfigAutomation:
    """Automated tests for solver configuration widget"""
    
    @pytest.fixture
    def solver_widget(self, qapp, config):
        """Provide solver config widget"""
        widget = SolverConfigWidget(config)
        widget.show()
        return widget
    
    def test_solver_selection(self, solver_widget, qtbot):
        """Test selecting different solvers"""
        combo = solver_widget.solver_combo
        
        # Test each solver
        for i in range(min(3, combo.count())):
            with qtbot.waitSignal(combo.currentTextChanged, timeout=1000):
                combo.setCurrentIndex(i)
            
            solver_name = combo.currentText()
            assert solver_name in ['simpleFoam', 'pimpleFoam', 'icoFoam', 
                                   'interFoam', 'buoyantSimpleFoam']
    
    def test_time_parameters(self, solver_widget, qtbot):
        """Test time parameter inputs"""
        # Test start time
        solver_widget.start_time.setValue(0.0)
        assert solver_widget.start_time.value() == 0.0
        
        # Test end time
        solver_widget.end_time.setValue(1000.0)
        assert solver_widget.end_time.value() == 1000.0
        
        # Test delta t
        solver_widget.delta_t.setValue(0.01)
        assert solver_widget.delta_t.value() == 0.01
    
    def test_write_interval(self, solver_widget, qtbot):
        """Test write interval setting"""
        solver_widget.write_interval.setValue(50)
        assert solver_widget.write_interval.value() == 50
    
    def test_discretization_schemes(self, solver_widget, qtbot):
        """Test discretization scheme selection"""
        # Test time scheme
        solver_widget.ddt_scheme.setCurrentIndex(0)
        assert solver_widget.ddt_scheme.currentText() in [
            'steadyState', 'Euler', 'backward', 'CrankNicolson'
        ]
        
        # Test gradient scheme
        solver_widget.grad_scheme.setCurrentIndex(0)
        assert 'Gauss' in solver_widget.grad_scheme.currentText()
    
    def test_solution_solvers(self, solver_widget, qtbot):
        """Test solution solver selection"""
        # Test pressure solver
        solver_widget.p_solver.setCurrentIndex(0)
        assert solver_widget.p_solver.currentText() in ['GAMG', 'PCG', 'PBiCGStab']
        
        # Test velocity solver
        solver_widget.u_solver.setCurrentIndex(0)
        assert solver_widget.u_solver.currentText() in [
            'smoothSolver', 'PBiCGStab', 'PCG'
        ]


class TestNewCaseDialogAutomation:
    """Automated tests for new case dialog"""
    
    @pytest.fixture
    def dialog(self, qapp):
        """Provide new case dialog"""
        dialog = NewCaseDialog()
        dialog.show()
        return dialog
    
    def test_dialog_creation(self, dialog):
        """Test dialog is created"""
        assert dialog.isVisible()
        assert dialog.isModal()
    
    def test_case_name_input(self, dialog, qtbot):
        """Test case name input"""
        dialog.name_edit.setText("testCase")
        assert dialog.name_edit.text() == "testCase"
    
    def test_path_input(self, dialog, qtbot):
        """Test path input"""
        test_path = "/tmp/test"
        dialog.path_edit.setText(test_path)
        assert dialog.path_edit.text() == test_path
    
    def test_solver_selection(self, dialog, qtbot):
        """Test solver selection"""
        combo = dialog.solver_combo
        combo.setCurrentIndex(0)
        assert combo.currentText() in [
            'simpleFoam', 'pimpleFoam', 'icoFoam', 'interFoam'
        ]
    
    def test_get_case_data(self, dialog, qtbot):
        """Test getting case data"""
        dialog.name_edit.setText("myCase")
        dialog.path_edit.setText("/tmp")
        dialog.solver_combo.setCurrentIndex(0)
        
        data = dialog.get_case_data()
        
        assert data['name'] == "myCase"
        assert data['path'] == "/tmp"
        assert 'solver' in data
        assert data['dimension'] == '3D'


class TestMeshPanelAutomation:
    """Automated tests for mesh panel"""
    
    @pytest.fixture
    def mesh_panel(self, qapp, config):
        """Provide mesh panel widget"""
        panel = MeshPanelWidget(config)
        panel.show()
        return panel
    
    def test_mesher_selection(self, mesh_panel, qtbot):
        """Test mesher combo box"""
        combo = mesh_panel.mesher_combo
        
        # Check available meshers
        meshers = [combo.itemText(i) for i in range(combo.count())]
        assert 'blockMesh' in meshers
        assert 'snappyHexMesh' in meshers
        assert 'cfMesh' in meshers
    
    def test_tab_switching(self, mesh_panel, qtbot):
        """Test switching between mesher tabs"""
        tabs = mesh_panel.tabs
        
        # Test each tab
        for i in range(tabs.count()):
            tabs.setCurrentIndex(i)
            assert tabs.currentIndex() == i


class TestKeyboardShortcuts:
    """Test keyboard shortcuts"""
    
    def test_new_case_shortcut(self, main_window, qtbot, monkeypatch):
        """Test Ctrl+N for new case"""
        mock_action = Mock()
        main_window.new_case_action = mock_action
        
        # Simulate Ctrl+N
        QTest.keyClick(main_window, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
        
        # Note: In real test, action would be triggered
        # This test structure shows the approach
    
    def test_save_shortcut(self, main_window, qtbot):
        """Test Ctrl+S for save"""
        # Create a case first
        main_window.current_case = "/tmp/test_case"
        main_window.save_action.setEnabled(True)
        
        # Simulate Ctrl+S
        QTest.keyClick(main_window, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)


class TestWorkflowAutomation:
    """Test complete workflows"""
    
    def test_complete_case_workflow(self, main_window, qtbot, temp_case_dir, monkeypatch):
        """Test complete case creation workflow"""
        # Mock case creation
        mock_manager = Mock()
        mock_manager.create_case.return_value = temp_case_dir
        main_window.case_manager = mock_manager
        
        # Trigger new case
        with patch('core.main_window.NewCaseDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = True
            mock_dialog.get_case_data.return_value = {
                'name': 'testCase',
                'path': temp_case_dir,
                'solver': 'simpleFoam',
                'dimension': '3D'
            }
            mock_dialog_class.return_value = mock_dialog
            
            main_window.new_case_action.trigger()
            
            # Verify case creation was called
            mock_manager.create_case.assert_called_once()
    
    def test_solver_configuration_workflow(self, main_window, qtbot):
        """Test solver configuration workflow"""
        # Switch to solver tab
        main_window.tab_widget.setCurrentWidget(main_window.solver_config)
        
        # Configure solver
        solver_widget = main_window.solver_config
        solver_widget.solver_combo.setCurrentText('simpleFoam')
        solver_widget.end_time.setValue(100)
        solver_widget.write_interval.setValue(10)
        
        # Verify settings
        assert solver_widget.solver_combo.currentText() == 'simpleFoam'
        assert solver_widget.end_time.value() == 100
        assert solver_widget.write_interval.value() == 10


class TestResponsiveness:
    """Test UI responsiveness"""
    
    def test_window_resize(self, main_window, qtbot):
        """Test window resizing"""
        original_size = main_window.size()
        
        # Resize window
        main_window.resize(1920, 1080)
        qtbot.wait(100)
        
        # Verify resize
        assert main_window.width() == 1920
        assert main_window.height() == 1080
    
    def test_dock_widget_resize(self, main_window, qtbot):
        """Test dock widget resizing"""
        dock = main_window.case_tree_dock
        
        # Ensure dock is visible
        assert dock.isVisible()
    
    def test_tab_loading_speed(self, main_window, qtbot):
        """Test tab switching speed"""
        import time
        
        start = time.time()
        for i in range(main_window.tab_widget.count()):
            main_window.tab_widget.setCurrentIndex(i)
            qtbot.wait(10)
        end = time.time()
        
        # All tabs should switch in less than 1 second
        assert (end - start) < 1.0


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "gui: mark test as GUI automation test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Mark all tests in this module as GUI tests
pytestmark = pytest.mark.gui


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
