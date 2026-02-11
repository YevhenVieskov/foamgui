"""
CAFFA Matplotlib Viewer
A working alternative viewer using matplotlib (no PyQt/VTK required)
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from caffa_reader import CAFFAReader, create_sample_data
from typing import Optional


class CAFFAMatplotlibViewer:
    """CAFFA viewer using Matplotlib and Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CAFFA CFD Viewer - Matplotlib Edition")
        self.root.geometry("1400x800")
        
        self.reader = CAFFAReader()
        self.current_data = None
        self.current_field = 'velocity_magnitude'
        
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - controls
        left_frame = ttk.Frame(main_container, width=250)
        self.create_control_panel(left_frame)
        main_container.add(left_frame, weight=1)
        
        # Center - plot area
        center_frame = ttk.Frame(main_container)
        self.create_plot_area(center_frame)
        main_container.add(center_frame, weight=4)
        
        # Right panel - info
        right_frame = ttk.Frame(main_container, width=250)
        self.create_info_panel(right_frame)
        main_container.add(right_frame, weight=1)
        
        # Menu bar
        self.create_menu()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Result File...", command=self.open_file)
        file_menu.add_command(label="Load Sample Data", command=self.load_sample_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Figure...", command=self.export_figure)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset View", command=self.reset_view)
        view_menu.add_command(label="Refresh", command=self.update_plot)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_control_panel(self, parent):
        """Create control panel"""
        parent.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Field selection
        field_frame = ttk.LabelFrame(parent, text="Field Selection", padding=10)
        field_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(field_frame, text="Variable:").pack()
        self.field_var = tk.StringVar(value="Velocity Magnitude")
        field_combo = ttk.Combobox(
            field_frame,
            textvariable=self.field_var,
            values=[
                "Velocity Magnitude",
                "U Velocity",
                "V Velocity",
                "Pressure",
                "Temperature",
                "Turbulent Kinetic Energy",
                "Dissipation"
            ],
            state="readonly"
        )
        field_combo.pack(fill=tk.X, pady=5)
        field_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        # Visualization options
        vis_frame = ttk.LabelFrame(parent, text="Visualization", padding=10)
        vis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.show_contours_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            vis_frame,
            text="Show Contours",
            variable=self.show_contours_var,
            command=self.update_plot
        ).pack(anchor=tk.W)
        
        self.show_vectors_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            vis_frame,
            text="Show Vectors",
            variable=self.show_vectors_var,
            command=self.update_plot
        ).pack(anchor=tk.W)
        
        self.show_streamlines_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            vis_frame,
            text="Show Streamlines",
            variable=self.show_streamlines_var,
            command=self.update_plot
        ).pack(anchor=tk.W)
        
        self.show_mesh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            vis_frame,
            text="Show Mesh",
            variable=self.show_mesh_var,
            command=self.update_plot
        ).pack(anchor=tk.W)
        
        # Contour settings
        contour_frame = ttk.LabelFrame(parent, text="Contour Settings", padding=10)
        contour_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(contour_frame, text="Number of Levels:").pack()
        self.num_contours_var = tk.IntVar(value=20)
        contour_spin = ttk.Spinbox(
            contour_frame,
            from_=5,
            to=50,
            textvariable=self.num_contours_var,
            command=self.update_plot,
            width=10
        )
        contour_spin.pack()
        
        # Colormap selection
        ttk.Label(contour_frame, text="Colormap:").pack(pady=(10, 0))
        self.cmap_var = tk.StringVar(value="jet")
        cmap_combo = ttk.Combobox(
            contour_frame,
            textvariable=self.cmap_var,
            values=["jet", "viridis", "plasma", "coolwarm", "rainbow", "turbo"],
            state="readonly",
            width=10
        )
        cmap_combo.pack()
        cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        # Vector settings
        vector_frame = ttk.LabelFrame(parent, text="Vector Settings", padding=10)
        vector_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(vector_frame, text="Density:").pack()
        self.vector_density_var = tk.IntVar(value=10)
        ttk.Spinbox(
            vector_frame,
            from_=5,
            to=30,
            textvariable=self.vector_density_var,
            command=self.update_plot,
            width=10
        ).pack()
        
    def create_plot_area(self, parent):
        """Create matplotlib plot area"""
        parent.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('CAFFA CFD Results')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def create_info_panel(self, parent):
        """Create information panel"""
        parent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Dataset info
        info_frame = ttk.LabelFrame(parent, text="Dataset Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Field Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=15, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
    def open_file(self):
        """Open CAFFA result file"""
        filename = filedialog.askopenfilename(
            title="Open CAFFA Result File",
            filetypes=[("CAFFA Results", "*.pos"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.current_data = self.reader.read_binary_file(filename)
                self.update_info()
                self.update_plot()
                self.root.title(f"CAFFA Viewer - {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def load_sample_data(self):
        """Load sample data"""
        try:
            self.current_data = create_sample_data(50, 30)
            self.update_info()
            self.update_plot()
            self.root.title("CAFFA Viewer - Sample Data")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sample data:\n{str(e)}")
    
    def update_plot(self):
        """Update the plot"""
        if self.current_data is None:
            return
        
        self.ax.clear()
        
        # Get coordinates
        x, y = self.reader.get_coordinates()
        
        # Map field name
        field_map = {
            "Velocity Magnitude": "vmag",
            "U Velocity": "u",
            "V Velocity": "v",
            "Pressure": "p",
            "Temperature": "t",
            "Turbulent Kinetic Energy": "te",
            "Dissipation": "dissipation"
        }
        
        field_name = field_map[self.field_var.get()]
        data = self.reader.get_cell_centered_data(field_name)
        
        # Show contours
        if self.show_contours_var.get():
            levels = self.num_contours_var.get()
            contour = self.ax.contourf(
                x, y, data,
                levels=levels,
                cmap=self.cmap_var.get()
            )
            self.fig.colorbar(contour, ax=self.ax, label=self.field_var.get())
        
        # Show mesh
        if self.show_mesh_var.get():
            self.ax.plot(x, y, 'k-', linewidth=0.3, alpha=0.3)
            self.ax.plot(x.T, y.T, 'k-', linewidth=0.3, alpha=0.3)
        
        # Show vectors
        if self.show_vectors_var.get():
            density = self.vector_density_var.get()
            u_2d = self.reader.get_cell_centered_data('u')
            v_2d = self.reader.get_cell_centered_data('v')
            
            # Subsample for vectors
            step = max(1, len(x) // density)
            self.ax.quiver(
                x[::step, ::step],
                y[::step, ::step],
                u_2d[::step, ::step],
                v_2d[::step, ::step],
                scale=20,
                color='black',
                alpha=0.7
            )
        
        # Show streamlines
        if self.show_streamlines_var.get():
            u_2d = self.reader.get_cell_centered_data('u')
            v_2d = self.reader.get_cell_centered_data('v')
            
            self.ax.streamplot(
                x, y, u_2d, v_2d,
                color='black',
                linewidth=1,
                density=1.5,
                arrowsize=1
            )
        
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title(f'CAFFA CFD Results - {self.field_var.get()}')
        self.ax.set_aspect('equal')
        
        self.canvas.draw()
        
        # Update statistics
        self.update_statistics(data)
    
    def update_info(self):
        """Update dataset information"""
        if self.current_data is None:
            return
        
        grid = self.current_data.grid
        
        info = f"""Dataset Information:

Time Step: {self.current_data.itim}
Physical Time: {self.current_data.time:.6f}

Grid:
  NI: {grid.ni}
  NJ: {grid.nj}
  Total Cells: {grid.nij}

Domain:
  X Range: [{np.min(grid.xc):.4f}, {np.max(grid.xc):.4f}]
  Y Range: [{np.min(grid.yc):.4f}, {np.max(grid.yc):.4f}]
"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
    
    def update_statistics(self, data):
        """Update field statistics"""
        stats = f"""Field Statistics:

Variable: {self.field_var.get()}

Minimum: {np.min(data):.6e}
Maximum: {np.max(data):.6e}
Mean: {np.mean(data):.6e}
Std Dev: {np.std(data):.6e}
Range: {np.max(data) - np.min(data):.6e}

Number of Points: {data.size}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
    
    def export_figure(self):
        """Export figure to file"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Figure",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("PDF Document", "*.pdf"),
                ("SVG Vector", "*.svg"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Figure saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save figure:\n{str(e)}")
    
    def reset_view(self):
        """Reset plot view"""
        if self.ax:
            self.ax.autoscale()
            self.canvas.draw()
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About CAFFA Viewer",
            "CAFFA CFD Visualization Tool\n"
            "Matplotlib Edition\n\n"
            "A tool for viewing CAFFA results\n"
            "using Matplotlib and Tkinter\n\n"
            "Compatible with Python 3.6+"
        )


def main():
    """Main entry point"""
    root = tk.Tk()
    app = CAFFAMatplotlibViewer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
