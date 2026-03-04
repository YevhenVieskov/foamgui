"""
Tests for Residual Plot Widget
"""

import pytest
import sys
from qtpy.QtWidgets import QApplication
from gui.residual_plot import ResidualPlotWidget
from gui.data_loader import CFDDataLoader

class TestResidualPlotWidget:
    """Tests for residual plot"""
    
    @pytest.fixture(scope='module')
    def app(self):
        """Create QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    
    @pytest.fixture
    def residual_widget(self, app):
        """Create residual widget"""
        widget = ResidualPlotWidget()
        widget.show()
        return widget
    
    def test_widget_initialization(self, residual_widget):
        """Test widget initializes"""
        assert residual_widget is not None
        assert residual_widget.figure is not None
    
    def test_update_residuals(self, residual_widget):
        """Test residual update"""
        loader = CFDDataLoader()
        sample_residuals = loader.generate_sample_residuals(10)
        residual_widget.update_residuals(sample_residuals)
        assert len(residual_widget.iterations) == 10
    
    def test_clear_plot(self, residual_widget):
        """Test plot clearing"""
        residual_widget._clear_plot()
        assert len(residual_widget.iterations) == 0
    
    def test_toggle_log_scale(self, residual_widget):
        """Test log scale toggle"""
        ax = residual_widget.figure.axes[0]
        initial_scale = ax.get_yscale()
        residual_widget._toggle_log_scale()
        assert ax.get_yscale() != initial_scale
    
    def teardown_method(self, method):
        """Cleanup"""
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])