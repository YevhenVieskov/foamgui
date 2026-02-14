"""
Real-time residual monitoring widget
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QComboBox
from PyQt6.QtCore import QTimer, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from pathlib import Path
import re
from collections import defaultdict


class ResidualMonitorWidget(QWidget):
    """Widget for real-time residual monitoring"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.case_path = None
        self.residuals = defaultdict(list)
        self.iterations = []
        self.monitoring = False
        
        self._create_ui()
        
        # Setup monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_residuals)
    
    def _create_ui(self):
        """Create user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls = QHBoxLayout()
        
        self.auto_scale_check = QCheckBox("Auto Scale")
        self.auto_scale_check.setChecked(True)
        controls.addWidget(self.auto_scale_check)
        
        controls.addWidget(QLabel("Log Scale:"))
        self.log_scale_combo = QComboBox()
        self.log_scale_combo.addItems(['Off', 'Y-axis', 'Both'])
        self.log_scale_combo.currentTextChanged.connect(self._update_plot_scale)
        controls.addWidget(self.log_scale_combo)
        
        controls.addWidget(QLabel("History:"))
        self.history_combo = QComboBox()
        self.history_combo.addItems(['100', '500', '1000', '5000', 'All'])
        self.history_combo.setCurrentText('1000')
        controls.addWidget(self.history_combo)
        
        self.clear_btn = QLabel("<a href='#'>Clear</a>")
        self.clear_btn.linkActivated.connect(self._clear_data)
        controls.addWidget(self.clear_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Matplotlib figure
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.ax.set_xlabel('Iteration')
        self.ax.set_ylabel('Residual')
        self.ax.set_title('Solver Residuals')
        self.ax.grid(True, alpha=0.3)
        
        layout.addWidget(self.canvas)
        
        # Legend checkboxes
        self.legend_layout = QHBoxLayout()
        layout.addLayout(self.legend_layout)
        
        self.field_checks = {}
    
    def start_monitoring(self, case_path: str):
        """Start monitoring residuals"""
        self.case_path = Path(case_path)
        self.monitoring = True
        
        interval = int(self.config.get('monitoring_interval', 1.0) * 1000)
        self.monitor_timer.start(interval)
    
    def stop_monitoring(self):
        """Stop monitoring residuals"""
        self.monitoring = False
        self.monitor_timer.stop()
    
    def _update_residuals(self):
        """Update residuals from log file"""
        if not self.case_path or not self.monitoring:
            return
        
        # Find solver log file
        log_files = list(self.case_path.glob('log.*'))
        if not log_files:
            return
        
        log_file = log_files[0]
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Parse residuals
            self._parse_residuals(lines)
            
            # Update plot
            self._update_plot()
            
        except Exception as e:
            print(f"Error reading log file: {e}")
    
    def _parse_residuals(self, lines: list):
        """Parse residuals from log lines"""
        # Pattern for OpenFOAM residuals
        # Time = 1
        # smoothSolver:  Solving for Ux, Initial residual = 0.999, Final residual = 0.001, No Iterations 10
        
        current_time = None
        
        for line in lines:
            # Check for time step
            time_match = re.search(r'Time\s*=\s*(\d+\.?\d*)', line)
            if time_match:
                current_time = float(time_match.group(1))
                if current_time not in self.iterations:
                    self.iterations.append(current_time)
                continue
            
            # Check for residuals
            residual_match = re.search(
                r'Solving for (\w+),.*Initial residual = ([\d.e+-]+)',
                line
            )
            
            if residual_match and current_time is not None:
                field = residual_match.group(1)
                residual = float(residual_match.group(2))
                
                # Ensure lists are same length
                while len(self.residuals[field]) < len(self.iterations) - 1:
                    self.residuals[field].append(None)
                
                self.residuals[field].append(residual)
                
                # Add checkbox for field if not exists
                if field not in self.field_checks:
                    self._add_field_checkbox(field)
    
    def _add_field_checkbox(self, field: str):
        """Add checkbox for field"""
        checkbox = QCheckBox(field)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(self._update_plot)
        
        self.field_checks[field] = checkbox
        self.legend_layout.addWidget(checkbox)
    
    def _update_plot(self):
        """Update residuals plot"""
        self.ax.clear()
        
        if not self.iterations:
            self.canvas.draw()
            return
        
        # Get history limit
        history_text = self.history_combo.currentText()
        if history_text == 'All':
            history_limit = len(self.iterations)
        else:
            history_limit = int(history_text)
        
        # Plot each field
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
        color_idx = 0
        
        for field, values in self.residuals.items():
            if field in self.field_checks and self.field_checks[field].isChecked():
                # Get data within history limit
                start_idx = max(0, len(self.iterations) - history_limit)
                x_data = self.iterations[start_idx:]
                y_data = values[start_idx:]
                
                # Filter out None values
                valid_data = [(x, y) for x, y in zip(x_data, y_data) if y is not None]
                if valid_data:
                    x_valid, y_valid = zip(*valid_data)
                    self.ax.plot(x_valid, y_valid, '-o', label=field, 
                               color=colors[color_idx % len(colors)], 
                               markersize=3, linewidth=1.5)
                    color_idx += 1
        
        # Set scale
        log_scale = self.log_scale_combo.currentText()
        if log_scale == 'Y-axis' or log_scale == 'Both':
            self.ax.set_yscale('log')
        if log_scale == 'Both':
            self.ax.set_xscale('log')
        
        self.ax.set_xlabel('Iteration')
        self.ax.set_ylabel('Residual')
        self.ax.set_title('Solver Residuals')
        self.ax.grid(True, alpha=0.3, which='both')
        self.ax.legend(loc='upper right')
        
        if self.auto_scale_check.isChecked():
            self.ax.relim()
            self.ax.autoscale_view()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _update_plot_scale(self):
        """Update plot scale"""
        self._update_plot()
    
    def _clear_data(self):
        """Clear residual data"""
        self.residuals.clear()
        self.iterations.clear()
        
        # Remove field checkboxes
        for checkbox in self.field_checks.values():
            self.legend_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        
        self.field_checks.clear()
        self._update_plot()
