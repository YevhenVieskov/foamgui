import tecplot as tp
from tecplot.constant import *
import os

# IMPORTANT NOTES:
# - Run this script connected to Tecplot 360 (use `python -m tecplot -b script.py` or connect via tp.session.connect()).
# - Adjust paths, variable names, and Z-position as needed for your case.
# - Assumes OpenFOAM case has variables: p, U (vector: U[X], U[Y], U[Z]), vorticity (component, e.g., vorticityZ or vorticity), vorticityMagnitude.
# - If vorticity is not present, you may need to compute it using tp.data.alter.create_variable().
# - Vortex core extraction uses the CFD Analyzer (Eigenmode method); it works best in 3D but can be applied to quasi-2D.
# - Animations export PNG sequences per variable (combine to video using ffmpeg or similar, e.g., ffmpeg -framerate 1 -i img_%04d.png -c:v libx264 anim.mp4).
# - Drag/lift plots require force integration over time; a basic setup is provided assuming pre-computed time-series data or manual integration.
# - Colormap uses 21 levels for contours (adjust colormap name as desired).
# - For scientific journal quality: serif fonts, high resolution exports, legends enabled.

# ========================
# 1. Load OpenFOAM case
# ========================
control_dict_path = 'path/to/your/openfoam/case/system/controlDict'  # CHANGE THIS TO YOUR CASE
tp.data.load_openfoam(control_dict_path)

dataset = tp.active_dataset()
print(f"Loaded dataset with {len(dataset.solution_times)} time steps.")

# Compute U Magnitude if not present
if 'U Magnitude' not in dataset.variable_names:
    tp.data.alter.create_variable(
        variable_name='U Magnitude',
        equation='sqrt({U[X]}**2 + {U[Y]}**2 + {U[Z]}**2)'
    )

# Assume variable names (adjust if different, e.g., 'vorticityZ' instead of 'vorticity')
var_p = 'p'
var_u = 'U Magnitude'
var_vort = 'vorticity'          # scalar vorticity (component)
var_vort_mag = 'vorticityMagnitude'

# ========================
# 2. Create XY plane slice (Z = constant, assume mid-plane)
# ========================
frame = tp.active_frame()
frame.plot_type = PlotType.Cartesian3D  # Use Cartesian2D if purely 2D

plot = frame.plot()
plot.show_slices = True
sl = plot.slice(0)
sl.show = True
sl.orientation = SliceSurface.ZPlanes
sl.z_position = 0.0  # CHANGE if your cylinder mid-plane is not Z=0
sl.edge.show = False
sl.mesh.show = False
sl.contour.show = True  # contours on slice

# Optional: extract slice as new zone for cleaner plotting (recommended for performance)
# extracted_zone = tp.data.extract.slice(sl.extract(), extract_blanked=False)
# Then activate and style the extracted zone

# ========================
# 3-4. Setup common contour style (filled + lines, 21 levels/colormap)
# ========================
plot.show_contour = True
contour = plot.contour(0)
contour.show = True
contour.flood = Flood.On
contour.lines = Lines.On
contour.num_levels = 21
contour.colormap.name = 'Rainbow'  # Options: 'Diverging - Blue/Red', 'Hot Metal', etc.
contour.legend.show = True
contour.legend.box.show = True
contour.legend.title.text = 'Variable'

# Set view to fit data
plot.view.fit()
plot.view.center = (0, 0, 0)  # assume cylinder at origin

# Hide unnecessary (e.g., volume mesh if 3D)
plot.show_mesh = False
plot.show_shade = False

# ========================
# Helper: Setup for specific plots
# ========================
def setup_contour(var_name, min_val=None, max_val=None):
    contour.variable = dataset.variable(var_name)
    if min_val is not None and max_val is not None:
        contour.levels.set_to_linear(min_val, max_val, 21)
    else:
        contour.levels.reset_to_nice()
    plot.title.text = f"{var_name} - t = {{SOLUTIONTIME}} s"
    tp.redraw()

def setup_vort_with_streamlines(var_name, min_val, max_val):
    setup_contour(var_name, min_val, max_val)
    plot.show_streamtraces = True
    plot.streamtraces.color = Color.Black
    plot.streamtraces.line_thickness = 0.4
    plot.streamtraces.arrowhead.show = True
    plot.streamtraces.arrowhead.size = 2.5
    plot.streamtraces.arrowhead.angle = 20
    # Add streamtraces (example: rake from freestream left side; adjust positions)
    # Here, simple example starting points across inlet (adjust coordinates)
    start_points = [(x, 0, 0) for x in [-10, -9, -8, -7, -6]]  # CHANGE to your domain inlet
    tp.active_frame().plot().streamtraces.add_streamtraces(
        tp.data.PointSet(start_points),
        stream_type=Streamtraces.SurfaceLine,
        direction=StreamDirection.ForwardAndBackward
    )
    tp.redraw()

# ========================
# 5. Find vortex cores (loop over time if needed)
# ========================
def extract_vortex_cores():
    # Set velocity components
    tp.macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer3'
      COMMAND = 'SetVelocityComponents XComponent = "U[X]" YComponent = "U[Y]" ZComponent = "U[Z]"'
    ''')
    # Extract vortex cores using Eigenmode method
    tp.macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer3'
      COMMAND = 'ExtractVortexCores Method = Eigenmode'
    ''')
    tp.redraw()
    print("Vortex cores extracted as new zone(s). Plot as scatter/line on vortex core zones.")

# Example: extract at one time (loop for all times if desired, but may create many zones)
plot.solution_time = 750.0  # example time
extract_vortex_cores()
# To plot centers: activate vortex core zone, enable scatter, style points

# ========================
# 6. Create animations (PNG sequences for time 700-800 s, step 1 s)
# ========================
start_time = 700
end_time = 800
step = 1
times = [t for t in dataset.solution_times if start_time <= t <= end_time and abs(t % step) < 1e-6]

def export_animation(var_name, folder, min_val=None, max_val=None, with_streamlines=False):
    os.makedirs(folder, exist_ok=True)
    for t in times:
        plot.solution_time = t
        if with_streamlines:
            setup_vort_with_streamlines(var_name, min_val, max_val)
        else:
            setup_contour(var_name, min_val, max_val)
        filename = os.path.join(folder, f"{var_name.replace(' ', '_')}_{int(t):04d}.png")
        tp.export.save_png(filename, width=1200, supersample=3)  # high quality
        print(f"Exported {filename}")
    print(f"Animation frames saved to {folder}. Combine with ffmpeg.")

# Export examples
export_animation(var_p, 'anim_p')
export_animation(var_u, 'anim_u')
export_animation(var_vort, 'anim_vort', min_val=-1, max_val=1)
export_animation(var_vort_mag, 'anim_vort_mag', min_val=0, max_val=1)
export_animation(var_vort, 'anim_vort_stream', min_val=-1, max_val=1, with_streamlines=True)
export_animation(var_vort_mag, 'anim_vort_mag_stream', min_val=0, max_val=1, with_streamlines=True)

# ========================
# 8. Create scene with multiple viewports (flow viz + drag/lift plots)
# ========================
# Example layout: 4 frames (adjust positions/sizes)
# Frame 1: p contour
# Frame 2: Vorticity with streamlines
# Frame 3-4: XY plots for drag/lift (assumes separate dataset loaded with 'Time', 'Drag', 'Lift')

tp.layout.frame.clear_all_frames()  # start fresh

# Flow viz frame (left large)
frame_flow = tp.layout.frame.add_frame(position=(0.05, 0.1, 0.6, 0.8))
frame_flow.activate()
frame_flow.plot_type = PlotType.Cartesian3D
# Setup contour (e.g., p or vorticity)
setup_contour(var_p)  # change as desired

# Vort with streamlines frame (right top)
frame_vort = tp.layout.frame.add_frame(position=(0.65, 0.55, 0.3, 0.35))
frame_vort.activate()
frame_vort.plot_type = PlotType.Cartesian3D
setup_vort_with_streamlines(var_vort, -1, 1)

# Drag plot (bottom left)
frame_drag = tp.layout.frame.add_frame(position=(0.05, 0.05, 0.4, 0.3))
frame_drag.activate()
frame_drag.plot_type = PlotType.XYLine
# Assume loaded dataset 'forces' with variables 'Time', 'Drag Coefficient'
# plot = frame_drag.plot()
# map = plot.mapping(0)
# map.x_variable = dataset.variable('Time')  # adjust dataset
# map.y_variable = dataset.variable('Drag Coefficient')
# map.line.color = Color.Blue
# map.line.line_thickness = 0.8
# plot.legend.show = True
# plot.x_axis.title.text = 'Time (s)'
# plot.y_axis.title.text = 'Drag Coefficient'

# Lift plot (bottom right) - similar to above

# Link frames by solution time
tp.layout.link_frames_by_solution_time(True)

# Final touches for journal quality
for fr in tp.layout.frames:
    fr.activate()
    pl = fr.plot()
    pl.axes.x_axis.title.font.family = FontFamily.Serif
    pl.axes.y_axis.title.font.family = FontFamily.Serif
    pl.axes.x_axis.title.font.size = 14
    pl.axes.y_axis.title.font.size = 14
    pl.frame.background_color = Color.White

tp.save_layout('cylinder_visualization.lay')
print("Layout saved. Open in Tecplot for final adjustments and export.")