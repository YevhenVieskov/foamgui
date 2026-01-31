import tecplot as tp
from tecplot.constant import *

# Connect to a live running instance of Tecplot 360
# (Or use tp.new_layout() if running in batch mode)
tp.session.connect()

frame = tp.active_frame()
plot = frame.plot()

print(f"Adjusting camera for Plot Type: {plot.plot_type.name}")

# ==============================================================================
# CASE A: Adjusting a 2D Plot (Cartesian2D)
# ==============================================================================
if plot.plot_type == PlotType.Cartesian2D:
    
    # 1. Fit to full data view
    print("Fitting view...")
    plot.view.fit()

    # 2. Zooming (Adjusting the View Width)
    # The 'width' property represents the width of the X-axis in data units currently visible.
    # Smaller width = Zoom In.
    current_width = plot.axes.x_axis.max - plot.axes.x_axis.min
    plot.view.width = current_width / 2.0  # Zoom in by 2x
    
    # 3. Panning (Moving the Center)
    # Set the (X, Y) coordinate that should be at the center of the viewport
    plot.view.center = (0.5, 0.0) 

# ==============================================================================
# CASE B: Adjusting a 3D Plot (Cartesian3D)
# ==============================================================================
elif plot.plot_type == PlotType.Cartesian3D:

    # 1. Standard Fit
    plot.view.fit()

    # 2. Setting Exact Camera Position and Target (Look-At)
    # 'position': Where the camera is located (x, y, z)
    # 'target': The point the camera is looking at (x, y, z)
    # 'up_vector': Which way is "up" (x, y, z)
    
    print("Setting specific 3D camera position...")
    plot.view.position = (10, 5, 5)
    plot.view.target = (0, 0, 0)     # Looking at origin
    plot.view.up_vector = (0, 0, 1)  # Z-axis is up

    # 3. Zooming
    # In 3D, 'width' is the field of view size.
    plot.view.width = 15.0

    # 4. Rotating using Spherical Coordinates (Psi, Theta, Alpha)
    # This is often easier than calculating X,Y,Z coordinates manually.
    # Psi: Angle from the up-vector (0-180)
    # Theta: Angle around the up-vector (0-360)
    # Alpha: Roll angle
    
    print("Rotating using spherical angles...")
    plot.view.psi = 60    # Elevation
    plot.view.theta = 45  # Azimuth / Rotation
    plot.view.alpha = 0   # Roll

    # 5. Isometric View (Standard Engineering View)
    # Tecplot doesn't have a single "iso" command, but you can set the angles:
    # plot.view.psi = 54.74
    # plot.view.theta = 45
    
# ==============================================================================
# UTILITY: Copy View from One Frame to Another
# ==============================================================================
def copy_view_style(source_frame_name, target_frame_name):
    """Copies camera settings from one frame to another."""
    try:
        src = tp.frame(source_frame_name)
        tgt = tp.frame(target_frame_name)
        
        # Capture view
        view = src.plot().view
        
        # Apply to target
        tgt.plot().view.position = view.position
        tgt.plot().view.target = view.target
        tgt.plot().view.width = view.width
        tgt.plot().view.psi = view.psi
        tgt.plot().view.theta = view.theta
        
        print(f"Copied view from {source_frame_name} to {target_frame_name}")
    except Exception as e:
        print(f"Error copying view: {e}")

# Trigger a redraw to see changes immediately
tp.active_page().redraw()

"""
Key Properties Cheat Sheet
Property	Description
plot.view.fit()	Resets the camera to fit all data zones.
plot.view.width	Controls zoom level. Smaller number = Zoom In.
plot.view.center	(2D) The (X, Y) coordinate at the center of the screen.
plot.view.position	(3D) The (X, Y, Z) location of the camera.
plot.view.target	(3D) The (X, Y, Z) point the camera is looking at (rotation center).
plot.view.psi	(3D) Elevation angle (tilt).
plot.view.theta	(3D) Azimuthal angle (rotation around vertical axis).
"""