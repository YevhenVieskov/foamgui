import tecplot as tp
from tecplot.constant import *

# ==============================================================================
# 1. SETUP & DATA LOADING
# ==============================================================================
tp.session.connect()
frame = tp.active_frame()
dataset = frame.dataset
plot = frame.plot()

# Ensure we are in 2D or 3D Cartesian mode
plot.plot_type = PlotType.Cartesian3D 
# Switch to 2D if your data is 2D:
# plot.plot_type = PlotType.Cartesian2D

# Define Vector Variables (U, V, W)
# Replace 'U', 'V', 'W' with your actual variable names
u_var = dataset.variable('U')
v_var = dataset.variable('V')
w_var = dataset.variable('W') # Optional for 2D

plot.vector.u_variable = u_var
plot.vector.v_variable = v_var
plot.vector.w_variable = w_var

# Turn on Streamtraces
plot.show_streamtraces = True
streamtraces = plot.streamtraces

# Clear existing streamtraces
streamtraces.delete_all()

# ==============================================================================
# FUNCTION 1: DRAW STREAMLINES
# Definition: Tangent to the velocity vector at a specific instant (snapshot).
# ==============================================================================
def draw_streamlines():
    print("Drawing Streamlines (Instantaneous)...")
    
    # 1. Set Timing Mode to Instantaneous
    streamtraces.timing.mode = StreamtraceTimingMode.Instantaneous
    
    # 2. Style (Lines)
    streamtraces.show_paths = True
    streamtraces.show_arrows = True
    streamtraces.color = Color.Blue
    streamtraces.line_thickness = 0.2
    
    # 3. Add a Rake (Line of start points)
    # Adjust coordinates (x, y, z) to match your domain
    streamtraces.add_rake(
        start_position=(-1, -1, 0),
        end_position=(-1, 1, 0),
        stream_type=Streamtrace.ThreeDLine
    )

# ==============================================================================
# FUNCTION 2: DRAW PATHLINES
# Definition: The trajectory of a single particle over a duration of time.
# ==============================================================================
def draw_pathlines(start_time, end_time):
    print("Drawing Pathlines (Time Integrated)...")
    
    # 1. Set Timing Mode to Actual (Uses Time Steps)
    streamtraces.timing.mode = StreamtraceTimingMode.Actual
    
    # 2. Configure Time Integration Range
    # This defines the lifespan of the particle calculation
    streamtraces.timing.start_time = start_time
    streamtraces.timing.end_time = end_time
    streamtraces.timing.anchor_time = start_time # Release particles at start
    
    # 3. Style (Red Trajectory)
    streamtraces.show_paths = True
    streamtraces.color = Color.Red
    streamtraces.line_thickness = 0.3
    streamtraces.show_arrows = False # Arrows often clutter pathlines
    
    # 4. Add Rake
    streamtraces.add_rake(
        start_position=(-1, -1, 0),
        end_position=(-1, 1, 0),
        stream_type=Streamtrace.ThreeDLine
    )

# ==============================================================================
# FUNCTION 3: DRAW STREAKLINES
# Definition: The locus of all particles that have passed through a point.
# In Tecplot, this is best visualized as continuously releasing markers.
# ==============================================================================
def draw_streaklines(start_time, end_time):
    print("Drawing Streaklines (Particle Injection)...")
    
    # 1. Set Timing Mode to Actual
    streamtraces.timing.mode = StreamtraceTimingMode.Actual
    
    # 2. Configure Timing for Continuous Release
    streamtraces.timing.start_time = start_time
    streamtraces.timing.end_time = end_time
    streamtraces.timing.anchor_time = start_time
    
    # 3. Style (Markers instead of Lines)
    # Streaklines are visually a "cloud" or "stream" of markers
    streamtraces.show_paths = False   # Turn off the connected line
    streamtraces.show_markers = True  # Turn on particles
    
    # 4. Marker Configuration
    # 'marker_interval' controls density of the streak
    streamtraces.timing.marker_interval = 0.1 # Every 0.1s a marker is calculated
    streamtraces.marker_symbol_type = SymbolType.Geometry
    streamtraces.marker_color = Color.Green
    streamtraces.marker_size = 1.5
    
    # 5. Add Rake (Injection Point)
    streamtraces.add_rake(
        start_position=(-1, -1, 0),
        end_position=(-1, 1, 0),
        stream_type=Streamtrace.ThreeDLine
    )

# ==============================================================================
# EXECUTION
# Uncomment the function you want to run.
# ==============================================================================

# Get solution time range from dataset
solution_times = [z.solution_time for z in dataset.zones()]
t_start = min(solution_times)
t_end = max(solution_times)

# 1. Streamlines (Snapshot at current time)
# draw_streamlines()

# 2. Pathlines (Full history of specific particles)
# draw_pathlines(t_start, t_end)

# 3. Streaklines (Simulating dye injection)
draw_streaklines(t_start, t_end)

# Redraw to see results
tp.active_page().redraw()