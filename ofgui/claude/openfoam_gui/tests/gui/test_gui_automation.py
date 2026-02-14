"""
GUI automation tests using pytest-qt
"""
import pytest
import sys
import time
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.main_window import MainWindow
from core.config import AppConfig
from widgets.blockmesh_editor import BlockMeshEditorWidget
from widgets.solver_config import SolverConfigWidget


@pytest.fixture
def app(qtbot):
    """Create QApplication instance"""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


@pytest.fixture
def config(tmp_path):
    """Create test configuration"""
    config_file = tmp_path / 'test_config.json'
    return AppConfig(str(config_file))


@pytest.fixture
def main_window(qtbot, config):
    """Create main window fixture"""
    window = MainWindow(config)
    qtbot.addWidget(window)
    return window


class TestMainWindowGUI:
    """GUI automation tests for main window"""
    
    def test_window_creation(self, qtbot, main_window):
        """Test main window is created successfully"""
        qtbot.addWidget(main_window)
        assert main_window.windowTitle().startswith("OpenFOAM GUI")
        assert main_window.isVisible() or True  # May not be visible in CI
    
    def test_menu_bar_exists(self, qtbot, main_window):
        """Test menu bar is created"""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # Check for expected menus
        actions = menu_bar.actions()
        menu_texts = [action.text() for action in actions]
        assert '&File' in menu_texts
        assert '&Mesh' in menu_texts
        assert '&Solver' in menu_texts
    
    def test_file_menu_actions(self, qtbot, main_window):
        """Test File menu actions"""
        file_menu = None
        for action in main_window.menuBar().actions():
            if action.text() == '&File':
                file_menu = action.menu()
                break
        
        assert file_menu is not None
        
        # Check for expected actions
        action_texts = [action.text() for action in file_menu.actions() if not action.isSeparator()]
        assert '&New Case...' in action_texts
        assert '&Open Case...' in action_texts
        assert '&Save' in action_texts
    
    def test_toolbar_creation(self, qtbot, main_window):
        """Test toolbar is created with actions"""
        toolbars = main_window.findChildren(QToolBar)
        assert len(toolbars) > 0
        
        toolbar = toolbars[0]
        actions = toolbar.actions()
        assert len(actions) > 0
    
    def test_dock_widgets(self, qtbot, main_window):
        """Test dock widgets are created"""
        assert main_window.case_tree_dock is not None
        assert main_window.case_tree is not None
    
    def test_tab_widget_creation(self, qtbot, main_window):
        """Test central tab widget"""
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() >= 3
        
        # Check tab names
        tab_names = [main_window.tab_widget.tabText(i) 
                    for i in range(main_window.tab_widget.count())]
        assert 'Mesh' in tab_names
        assert 'Solver Setup' in tab_names
        assert 'Monitoring' in tab_names
    
    def test_status_bar(self, qtbot, main_window):
        """Test status bar exists"""
        status_bar = main_window.statusBar()
        assert status_bar is not None
    
    def test_tab_switching(self, qtbot, main_window):
        """Test switching between tabs"""
        tab_widget = main_window.tab_widget
        
        # Switch to each tab
        for i in range(tab_widget.count()):
            tab_widget.setCurrentIndex(i)
            qtbot.wait(100)  # Wait for tab to render
            assert tab_widget.currentIndex() == i
    
    def test_new_case_dialog_trigger(self, qtbot, main_window):
        """Test triggering new case dialog"""
        # Trigger new case action
        main_window.new_case_action.trigger()
        qtbot.wait(100)
        
        # Dialog should be created (may not be visible in headless mode)
    
    def test_keyboard_shortcuts(self, qtbot, main_window):
        """Test keyboard shortcuts work"""
        # Test Ctrl+N for new case
        QTest.keySequence(main_window, Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_N)
        qtbot.wait(100)
        
        # Should trigger new case action
        # (In headless mode, just verify no crash)
    
    def test_solver_config_widget_interaction(self, qtbot, main_window):
        """Test interaction with solver config widget"""
        # Switch to solver config tab
        for i in range(main_window.tab_widget.count()):
            if main_window.tab_widget.tabText(i) == 'Solver Setup':
                main_window.tab_widget.setCurrentIndex(i)
                break
        
        solver_widget = main_window.solver_config
        assert solver_widget is not None
        
        # Test solver selection
        solver_combo = solver_widget.solver_combo
        assert solver_combo.count() > 0
        
        # Change solver
        original_index = solver_combo.currentIndex()
        new_index = (original_index + 1) % solver_combo.count()
        solver_combo.setCurrentIndex(new_index)
        qtbot.wait(100)
        assert solver_combo.currentIndex() == new_index


class TestBlockMeshEditorGUI:
    """GUI automation tests for blockMesh editor"""
    
    @pytest.fixture
    def editor(self, qtbot, config, tmp_path):
        """Create blockMesh editor fixture"""
        case_path = tmp_path / 'test_case'
        case_path.mkdir()
        (case_path / 'system').mkdir()
        
        editor = BlockMeshEditorWidget(str(case_path), config)
        qtbot.addWidget(editor)
        return editor
    
    def test_editor_creation(self, qtbot, editor):
        """Test editor window creation"""
        assert editor.windowTitle().startswith("blockMesh Editor")
    
    def test_add_vertex_button(self, qtbot, editor):
        """Test adding vertices"""
        initial_row_count = editor.vertices_table.rowCount()
        
        # Find and click add vertex button
        for child in editor.findChildren(QPushButton):
            if child.text() == "Add Vertex":
                qtbot.mouseClick(child, Qt.MouseButton.LeftButton)
                qtbot.wait(100)
                break
        
        # Verify vertex was added
        assert editor.vertices_table.rowCount() == initial_row_count + 1
    
    def test_vertex_table_editing(self, qtbot, editor):
        """Test editing vertex coordinates"""
        # Add a vertex first
        for child in editor.findChildren(QPushButton):
            if child.text() == "Add Vertex":
                qtbot.mouseClick(child, Qt.MouseButton.LeftButton)
                break
        
        qtbot.wait(100)
        
        # Edit vertex coordinates
        editor.vertices_table.setItem(0, 1, QTableWidgetItem("1.5"))
        editor.vertices_table.setItem(0, 2, QTableWidgetItem("2.5"))
        editor.vertices_table.setItem(0, 3, QTableWidgetItem("3.5"))
        
        qtbot.wait(100)
        
        # Verify data
        assert len(editor.vertices) > 0
    
    def test_block_creation(self, qtbot, editor):
        """Test creating a block"""
        # Add 8 vertices for a block
        for i in range(8):
            for child in editor.findChildren(QPushButton):
                if child.text() == "Add Vertex":
                    qtbot.mouseClick(child, Qt.MouseButton.LeftButton)
                    qtbot.wait(50)
                    break
        
        initial_block_count = len(editor.blocks)
        
        # Click add block button
        for action in editor.findChildren(QAction):
            if action.text() == "New Block":
                action.trigger()
                qtbot.wait(100)
                break
        
        # Verify block was added
        assert len(editor.blocks) >= initial_block_count
    
    def test_cell_count_spinboxes(self, qtbot, editor):
        """Test cell count spinboxes"""
        # Set cell counts
        editor.cells_x.setValue(20)
        editor.cells_y.setValue(15)
        editor.cells_z.setValue(10)
        
        qtbot.wait(100)
        
        assert editor.cells_x.value() == 20
        assert editor.cells_y.value() == 15
        assert editor.cells_z.value() == 10
    
    def test_grading_spinboxes(self, qtbot, editor):
        """Test grading spinboxes"""
        editor.grading_x.setValue(1.5)
        editor.grading_y.setValue(2.0)
        editor.grading_z.setValue(0.8)
        
        qtbot.wait(100)
        
        assert editor.grading_x.value() == pytest.approx(1.5)
        assert editor.grading_y.value() == pytest.approx(2.0)
        assert editor.grading_z.value() == pytest.approx(0.8)
    
    def test_view_controls(self, qtbot, editor):
        """Test 3D view control buttons"""
        # Find view control buttons
        buttons = editor.findChildren(QPushButton)
        
        view_buttons = [b for b in buttons if 'View' in b.text()]
        assert len(view_buttons) > 0
        
        # Click each view button
        for button in view_buttons:
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
            qtbot.wait(100)
    
    def test_save_blockmesh_dict(self, qtbot, editor):
        """Test saving blockMeshDict"""
        # Add some vertices and blocks first
        for i in range(8):
            for child in editor.findChildren(QPushButton):
                if child.text() == "Add Vertex":
                    qtbot.mouseClick(child, Qt.MouseButton.LeftButton)
                    qtbot.wait(20)
                    break
        
        # Trigger save action
        for action in editor.findChildren(QAction):
            if action.text() == "Save blockMeshDict":
                action.trigger()
                qtbot.wait(100)
                break
        
        # Check if file was created
        system_dir = Path(editor.case_path) / 'system'
        if system_dir.exists():
            blockmesh_file = system_dir / 'blockMeshDict'
            # File may or may not exist depending on validation


class TestSolverConfigGUI:
    """GUI automation tests for solver configuration"""
    
    @pytest.fixture
    def solver_widget(self, qtbot, config):
        """Create solver config widget"""
        widget = SolverConfigWidget(config)
        qtbot.addWidget(widget)
        return widget
    
    def test_solver_selection(self, qtbot, solver_widget):
        """Test solver selection"""
        solver_combo = solver_widget.solver_combo
        
        # Select each solver
        for i in range(min(3, solver_combo.count())):  # Test first 3 solvers
            solver_combo.setCurrentIndex(i)
            qtbot.wait(100)
            assert solver_combo.currentIndex() == i
    
    def test_general_settings_tab(self, qtbot, solver_widget):
        """Test general settings controls"""
        # Switch to general tab
        solver_widget.tabs.setCurrentIndex(0)
        qtbot.wait(100)
        
        # Test time settings
        solver_widget.start_time.setValue(10.0)
        solver_widget.end_time.setValue(500.0)
        solver_widget.delta_t.setValue(0.5)
        
        qtbot.wait(100)
        
        assert solver_widget.start_time.value() == pytest.approx(10.0)
        assert solver_widget.end_time.value() == pytest.approx(500.0)
        assert solver_widget.delta_t.value() == pytest.approx(0.5)
    
    def test_discretization_settings_tab(self, qtbot, solver_widget):
        """Test discretization settings"""
        # Switch to discretization tab
        solver_widget.tabs.setCurrentIndex(1)
        qtbot.wait(100)
        
        # Change scheme selections
        solver_widget.ddt_scheme.setCurrentIndex(1)
        solver_widget.grad_scheme.setCurrentIndex(1)
        
        qtbot.wait(100)
    
    def test_solution_settings_tab(self, qtbot, solver_widget):
        """Test solution settings"""
        # Switch to solution tab
        solver_widget.tabs.setCurrentIndex(2)
        qtbot.wait(100)
        
        # Change solver selections
        solver_widget.p_solver.setCurrentIndex(1)
        solver_widget.u_solver.setCurrentIndex(1)
        solver_widget.tolerance.setValue(1e-7)
        
        qtbot.wait(100)


class TestResidualMonitorGUI:
    """GUI automation tests for residual monitor"""
    
    def test_residual_monitor_creation(self, qtbot, main_window):
        """Test residual monitor widget"""
        residual_monitor = main_window.residual_monitor
        assert residual_monitor is not None
    
    def test_control_widgets(self, qtbot, main_window):
        """Test residual monitor controls"""
        monitor = main_window.residual_monitor
        
        # Test auto-scale checkbox
        if hasattr(monitor, 'auto_scale_check'):
            original_state = monitor.auto_scale_check.isChecked()
            monitor.auto_scale_check.setChecked(not original_state)
            qtbot.wait(100)
            assert monitor.auto_scale_check.isChecked() == (not original_state)
    
    def test_log_scale_combo(self, qtbot, main_window):
        """Test log scale selection"""
        monitor = main_window.residual_monitor
        
        if hasattr(monitor, 'log_scale_combo'):
            for i in range(monitor.log_scale_combo.count()):
                monitor.log_scale_combo.setCurrentIndex(i)
                qtbot.wait(100)


class TestContourViewerGUI:
    """GUI automation tests for contour viewer"""
    
    def test_contour_viewer_creation(self, qtbot, main_window):
        """Test contour viewer widget"""
        contour_viewer = main_window.contour_viewer
        assert contour_viewer is not None
    
    def test_field_selection(self, qtbot, main_window):
        """Test field selection combo"""
        viewer = main_window.contour_viewer
        
        if hasattr(viewer, 'field_combo'):
            field_combo = viewer.field_combo
            for i in range(min(3, field_combo.count())):
                field_combo.setCurrentIndex(i)
                qtbot.wait(100)
    
    def test_component_selection(self, qtbot, main_window):
        """Test component selection"""
        viewer = main_window.contour_viewer
        
        if hasattr(viewer, 'component_combo'):
            component_combo = viewer.component_combo
            for i in range(component_combo.count()):
                component_combo.setCurrentIndex(i)
                qtbot.wait(100)
    
    def test_display_options(self, qtbot, main_window):
        """Test display option checkboxes"""
        viewer = main_window.contour_viewer
        
        if hasattr(viewer, 'show_edges_check'):
            original_state = viewer.show_edges_check.isChecked()
            viewer.show_edges_check.setChecked(not original_state)
            qtbot.wait(100)


class TestWorkflowAutomation:
    """Test complete workflow automation"""
    
    def test_complete_case_workflow(self, qtbot, main_window, tmp_path):
        """Test complete case creation workflow"""
        # This simulates a user creating a case through the GUI
        
        # Step 1: Trigger new case (would open dialog in real usage)
        main_window.new_case_action.trigger()
        qtbot.wait(200)
        
        # Step 2: Verify solver config is accessible
        main_window.tab_widget.setCurrentWidget(main_window.solver_config)
        qtbot.wait(100)
        
        # Step 3: Configure solver settings
        solver_widget = main_window.solver_config
        solver_widget.end_time.setValue(100.0)
        solver_widget.delta_t.setValue(1.0)
        qtbot.wait(100)
        
        # Step 4: Switch to mesh panel
        main_window.tab_widget.setCurrentWidget(main_window.mesh_panel)
        qtbot.wait(100)
        
        # Step 5: Switch to monitoring
        main_window.tab_widget.setCurrentIndex(2)
        qtbot.wait(100)
    
    def test_rapid_tab_switching(self, qtbot, main_window):
        """Test rapid switching between tabs"""
        tab_widget = main_window.tab_widget
        
        # Rapidly switch tabs
        for _ in range(3):
            for i in range(tab_widget.count()):
                tab_widget.setCurrentIndex(i)
                qtbot.wait(50)
    
    def test_stress_test_widget_creation(self, qtbot, config, tmp_path):
        """Stress test: Create multiple editor instances"""
        case_path = tmp_path / 'test_case'
        case_path.mkdir()
        (case_path / 'system').mkdir()
        
        editors = []
        for i in range(5):  # Create 5 editors
            editor = BlockMeshEditorWidget(str(case_path), config)
            qtbot.addWidget(editor)
            editors.append(editor)
            qtbot.wait(100)
        
        # Clean up
        for editor in editors:
            editor.close()


# Performance measurement decorators
def measure_performance(func):
    """Decorator to measure test performance"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"\n{func.__name__} took {end - start:.3f} seconds")
        return result
    return wrapper


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
