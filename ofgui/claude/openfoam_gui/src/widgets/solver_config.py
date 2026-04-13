"""Solver configuration widget"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QComboBox, QLabel, QTabWidget, QFormLayout,
                              QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit)
from solvers.solver_registry import SolverRegistry


class SolverConfigWidget(QWidget):
    """Widget for configuring solver settings"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.case_path = None
        self.solver_registry = SolverRegistry()
        
        layout = QVBoxLayout(self)
        
        # Solver selection
        solver_layout = QHBoxLayout()
        solver_layout.addWidget(QLabel("Solver:"))
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(self.solver_registry.get_solver_list())
        self.solver_combo.currentTextChanged.connect(self._on_solver_changed)
        solver_layout.addWidget(self.solver_combo)
        solver_layout.addStretch()
        layout.addLayout(solver_layout)
        
        # Tabs for different configuration aspects
        self.tabs = QTabWidget()
        
        # General settings
        general_widget = self._create_general_settings()
        self.tabs.addTab(general_widget, "General")
        
        # Discretization
        discretization_widget = self._create_discretization_settings()
        self.tabs.addTab(discretization_widget, "Discretization")
        
        # Solution
        solution_widget = self._create_solution_settings()
        self.tabs.addTab(solution_widget, "Solution")
        
        layout.addWidget(self.tabs)
    
    def _create_general_settings(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.start_time = QDoubleSpinBox()
        self.start_time.setRange(0, 1e10)
        layout.addRow("Start Time:", self.start_time)
        
        self.end_time = QDoubleSpinBox()
        self.end_time.setRange(0, 1e10)
        self.end_time.setValue(1000)
        layout.addRow("End Time:", self.end_time)
        
        self.delta_t = QDoubleSpinBox()
        self.delta_t.setRange(1e-10, 1e10)
        self.delta_t.setValue(1.0)
        layout.addRow("Time Step:", self.delta_t)
        
        self.write_interval = QSpinBox()
        self.write_interval.setRange(1, 1000000)
        self.write_interval.setValue(100)
        layout.addRow("Write Interval:", self.write_interval)
        
        return widget
    
    def _create_discretization_settings(self) -> QWidget:
        """Create discretization settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.ddt_scheme = QComboBox()
        self.ddt_scheme.addItems(['steadyState', 'Euler', 'backward', 'CrankNicolson'])
        layout.addRow("Time Scheme:", self.ddt_scheme)
        
        self.grad_scheme = QComboBox()
        self.grad_scheme.addItems(['Gauss linear', 'leastSquares', 'cellLimited Gauss linear'])
        layout.addRow("Gradient Scheme:", self.grad_scheme)
        
        self.div_scheme = QComboBox()
        self.div_scheme.addItems(['Gauss upwind', 'Gauss linearUpwind', 'bounded Gauss upwind'])
        layout.addRow("Divergence Scheme:", self.div_scheme)
        
        return widget
    
    def _create_solution_settings(self) -> QWidget:
        """Create solution settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.p_solver = QComboBox()
        self.p_solver.addItems(['GAMG', 'PCG', 'PBiCGStab'])
        layout.addRow("Pressure Solver:", self.p_solver)
        
        self.u_solver = QComboBox()
        self.u_solver.addItems(['smoothSolver', 'PBiCGStab', 'PCG'])
        layout.addRow("Velocity Solver:", self.u_solver)
        
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(1e-15, 1e-3)
        self.tolerance.setValue(1e-6)
        self.tolerance.setDecimals(10)
        layout.addRow("Tolerance:", self.tolerance)
        
        return widget
    
    def load_case(self, case_path: str):
        """Load case configuration"""
        self.case_path = case_path
    
    def _on_solver_changed(self, solver: str):
        """Handle solver selection change"""
        # Update UI based on solver requirements
        pass
