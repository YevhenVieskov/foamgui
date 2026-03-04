"""
Functional Tests for Visualization Widget
"""

import pytest
import sys
from qtpy.QtWidgets import QApplication
from gui.visualization_widget import VisualizationWidget
from gui.data_loader import CFDDataLoader

class TestVisualizationWidget:
    """Functional tests for visualization"""
    
    @pytest.fixture(scope='module')
    def app(self):
        """Create QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    
    @pytest.fixture
    def viz_widget(self, app):
        """Create visualization widget"""
        widget = VisualizationWidget()
        widget.show()
        return widget
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data"""
        loader = CFDDataLoader()
        return {
            'mesh': loader._create_sample_mesh({}),
            'scalars': 'Pressure',
            'residuals': loader.generate_sample_residuals(10)
        }
    
    def test_widget_initialization(self, viz_widget):
        """Test widget initializes correctly"""
        assert viz_widget is not None
        assert viz_widget.plotter is not None
    
    def test_update_data(self, viz_widget, sample_data):
        """Test data update"""
        viz_widget.update_data(sample_data)
        assert viz_widget.current_data is not None
        assert viz_widget.current_data['mesh'] is not None
    
    def test_toggle_vectors(self, viz_widget, sample_data):
        """Test vector toggle"""
        viz_widget.update_data(sample_data)
        viz_widget.show_vectors(True)
        # Vector actor should be created
        viz_widget.show_vectors(False)
        # Vector actor should be removed
    
    def test_add_plane_section(self, viz_widget, sample_data):
        """Test plane section addition"""
        viz_widget.update_data(sample_data)
        initial_planes = len(viz_widget.planes)
        viz_widget.add_plane_section()
        assert len(viz_widget.planes) == initial_planes + 1
    
    def test_reset_camera(self, viz_widget):
        """Test camera reset"""
        viz_widget.reset_camera()
        # Should not raise exception
    
    def test_set_camera_view(self, viz_widget):
        """Test camera view setting"""
        viz_widget.set_camera_view("front")
        viz_widget.set_camera_view("top")
        viz_widget.set_camera_view("iso")
        # Should not raise exception
    
    def teardown_method(self, method):
        """Cleanup after each test"""
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])