"""
Residual Plot Widget - Star CCM+ Style
"""

from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from qtpy.QtCore import Signal, Slot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import csv

class ResidualPlotWidget(QWidget):
    """Residual monitoring widget with Star CCM+ style"""
    
    def __init__(self):
        super().__init__()
        self.residuals_data = {
            'u_momentum': [],
            'v_momentum': [],
            'mass': [],
            'energy': [],
            'turbulent_energy': [],
            'dissipation': []
        }
        self.iterations = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure (Star CCM+ style)
        self.figure = Figure(figsize=(10, 6), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white;")
        layout.addWidget(self.canvas)
        
        # Control panel
        control_panel = QHBoxLayout()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-top: 1px solid #cccccc;
                padding: 5px;
            }
        """)
        
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self._clear_plot)
        control_panel.addWidget(clear_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._export_data)
        control_panel.addWidget(export_btn)
        
        log_scale_btn = QPushButton("📊 Log Scale")
        log_scale_btn.setCheckable(True)
        log_scale_btn.setChecked(True)
        log_scale_btn.clicked.connect(self._toggle_log_scale)
        control_panel.addWidget(log_scale_btn)
        
        control_panel.addStretch()
        
        self.info_label = QLabel("Iterations: 0")
        control_panel.addWidget(self.info_label)
        
        layout.addLayout(control_panel)
        
        # Initialize plot
        self._initialize_plot()
    
    def _initialize_plot(self):
        """Initialize the residual plot"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Star CCM+ style
        ax.set_facecolor('white')
        self.figure.patch.set_facecolor('white')
        
        ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residual', fontsize=12, fontweight='bold')
        ax.set_title('Convergence History - CAFFA Simulation', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        # Set colors matching Star CCM+
        colors = ['#0078d7', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        labels = ['U-Momentum', 'V-Momentum', 'Mass', 'Energy', 'Turbulent Energy', 'Dissipation']
        
        for i, label in enumerate(labels):
            ax.plot([], [], color=colors[i], label=label, linewidth=2)
        
        ax.legend(loc='upper right', framealpha=0.9)
        
        # Add convergence criteria line
        ax.axhline(y=1e-4, color='gray', linestyle=':', alpha=0.5, label='Convergence Criteria')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    @Slot(list)
    def update_residuals(self, residuals):
        """Update residual plot with new data"""
        if not residuals:
            return
        
        # Parse residuals
        self.iterations = [r.get('iteration', i) for i, r in enumerate(residuals)]
        
        for key in self.residuals_data.keys():
            if key in residuals[0]:
                self.residuals_data[key] = [r.get(key, 1e-6) for r in residuals]
        
        self._plot_residuals()
        self.info_label.setText(f"Iterations: {len(self.iterations)}")
    
    def _plot_residuals(self):
        """Plot the residuals"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Star CCM+ style
        ax.set_facecolor('white')
        self.figure.patch.set_facecolor('white')
        
        colors = ['#0078d7', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        labels = ['U-Momentum', 'V-Momentum', 'Mass', 'Energy', 'Turbulent Energy', 'Dissipation']
        
        for i, (key, label) in enumerate(zip(self.residuals_data.keys(), labels)):
            if self.residuals_data[key]:
                ax.semilogy(
                    self.iterations,
                    self.residuals_data[key],
                    color=colors[i],
                    label=label,
                    linewidth=2,
                    marker='o',
                    markersize=3,
                    alpha=0.7
                )
        
        ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residual', fontsize=12, fontweight='bold')
        ax.set_title('Convergence History - CAFFA Simulation', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        ax.legend(loc='upper right', framealpha=0.9)
        
        # Add convergence criteria line
        ax.axhline(y=1e-4, color='gray', linestyle=':', alpha=0.5, label='Convergence Criteria')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _clear_plot(self):
        """Clear the plot"""
        self.residuals_data = {key: [] for key in self.residuals_data.keys()}
        self.iterations = []
        self._initialize_plot()
        self.info_label.setText("Iterations: 0")
    
    def _toggle_log_scale(self):
        """Toggle logarithmic scale"""
        ax = self.figure.axes[0]
        if ax.get_yscale() == 'log':
            ax.set_yscale('linear')
        else:
            ax.set_yscale('log')
        self.canvas.draw()
    
    def _export_data(self):
        """Export residual data to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Residuals",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    header = ['Iteration'] + list(self.residuals_data.keys())
                    writer.writerow(header)
                    
                    for i in self.iterations:
                        row = [i]
                        for key in self.residuals_data.keys():
                            if i < len(self.residuals_data[key]):
                                row.append(self.residuals_data[key][i])
                            else:
                                row.append('')
                        writer.writerow(row)
                
                print(f"Data exported to {filename}")
            except Exception as e:
                print(f"Export failed: {e}")
    
    def export_data(self, filename):
        """Export data (called from main window)"""
        self._export_data()