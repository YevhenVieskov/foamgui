import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
import pandas as pd
import numpy as np
import os

# ==============================================================================
# CONFIGURATION
# ==============================================================================
CASE_DIR = '.'  # Current directory containing OpenFOAM case
START_TIME = 700
END_TIME = 800
TIME_STEP = 1
FORCE_FILE_PATH = os.path.join(CASE_DIR, 'postProcessing/forceCoeffs/0/forceCoeffs.dat')

# Variables to animate
ANIMATION_VARS = [
    {'name': 'Pressure', 'var_name': 'p', 'min': -100, 'max': 100}, # Adjust P range as needed
    {'name': 'Velocity', 'var_name': 'U', 'min': 0, 'max': 15},     # Adjust U range
    {'name': 'VorticityZ', 'var_name': 'VorticityZ', 'min': -1, 'max': 1},
    {'name': 'VorticityMag', 'var_name': 'Magnitude Vorticity', 'min': 0, 'max': 1}
]

# Output Directory
OUTPUT_DIR = 'frames'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ==============================================================================
# 1. SETUP & DATA LOADING
# ==============================================================================
tp.session.connect()
tp.new_layout()
print("Connected to Tecplot...")

# Load OpenFOAM Case
# We use the .foam empty file method or controlDict
foam_file = [f for f in os.listdir(CASE_DIR) if f.endswith('.foam')]
if foam_file:
    data_file = foam_file[0]
else:
    data_file = 'case.foam' 
    with open(data_file, 'w') as f: pass

dataset = tp.data.load_openfoam(
    case_filenames=[data_file],
    boundary_zone_face_neighbor_mode=OpenFOAMBoundaryZoneFaceNeighborMode.PointMatch
)
print("Data loaded.")

# ==============================================================================
# 2. DATA CALCULATION (Vorticity & Q-Criterion)
# ==============================================================================
# Calculate Vorticity and Magnitude
tp.data.operate.execute_equation('{VorticityVec} = Curl({U})', value_location=ValueLocation.CellCentered)
tp.data.operate.execute_equation('{VorticityZ} = {VorticityVec}[3]', value_location=ValueLocation.CellCentered)
tp.data.operate.execute_equation('{Magnitude Vorticity} = SQRT({VorticityVec}[1]**2 + {VorticityVec}[2]**2 + {VorticityVec}[3]**2)', value_location=ValueLocation.CellCentered)

# Calculate Q-Criterion for Vortex Cores
tp.data.operate.execute_equation('{Q_Criterion} = QCriterion({U})', value_location=ValueLocation.CellCentered)

# Interpolate to nodes (required for high-quality contouring and streamlines)
tp.data.operate.interpolate_linear(dataset.zones())

# ==============================================================================
# 3. LAYOUT SETUP (Frames for Flow, Drag, Lift)
# ==============================================================================
page = tp.active_page()
page.name = 'Cylinder Flow Analysis'

# --- Frame 1: Flow Visualization (Top) ---
frame_flow = page.active_frame()
frame_flow.name = 'FlowViz'
frame_flow.position = (0.5, 3)
frame_flow.width = 8
frame_flow.height = 5
plot = frame_flow.plot(PlotType.Cartesian2D)
plot.activate()

# Set visual style for publication
plot.axes.x_axis.show = True
plot.axes.y_axis.show = True
plot.axes.x_axis.title.font.size = 2.5
plot.axes.y_axis.title.font.size = 2.5
plot.axes.x_axis.tick_labels.font.size = 2
plot.axes.y_axis.tick_labels.font.size = 2

# Slice/Section setup (OpenFOAM 2D is effectively a slice, but we ensure Z-plane)
# We turn off the mesh and set up the contour
plot.show_mesh = False
plot.show_contour = True
plot.show_shade = False # Use contour flood instead

# --- Load Force Data for XY Plots ---
try:
    # Skip header rows (#) and read standard OpenFOAM forceCoeffs columns
    # Expected: Time, Cm, Cd, Cl, Cl(f), Cl(r)
    df = pd.read_csv(FORCE_FILE_PATH, sep='\t', comment='#', header=None, 
                     names=['Time', 'Cm', 'Cd', 'Cl', 'Cl_f', 'Cl_r'], index_col=False)
    
    # Clean whitespace in columns if parsing failed slightly
    if len(df.columns) == 1: # Fallback for space-separated
        df = pd.read_csv(FORCE_FILE_PATH, delim_whitespace=True, comment='#', 
                         names=['Time', 'Cm', 'Cd', 'Cl', 'Cl_f', 'Cl_r'])
except Exception as e:
    print(f"Warning: Could not load force coefficients: {e}")
    df = pd.DataFrame({'Time': [0], 'Cd': [0], 'Cl': [0]})

# --- Frame 2: Drag Coefficient (Bottom Left) ---
frame_drag = page.add_frame()
frame_drag.position = (0.5, 0.5)
frame_drag.width = 3.8
frame_drag.height = 2
plot_drag = frame_drag.plot(PlotType.XYLine)
plot_drag.activate()

ds_drag = frame_drag.create_dataset('Drag Data', ['Time', 'Cd'])
zone_drag = ds_drag.add_ordered_zone('DragHistory', len(df))
zone_drag.values('Time')[:] = df['Time'].values
zone_drag.values('Cd')[:] = df['Cd'].values

linemap_drag = plot_drag.linemap(0)
linemap_drag.show = True
linemap_drag.zone = zone_drag
linemap_drag.line.color = Color.Blue
linemap_drag.line.line_thickness = 0.4
plot_drag.axes.x_axis.title.text = 'Time (s)'
plot_drag.axes.y_axis.title.text = 'Cd'
plot_drag.view.fit()

# --- Frame 3: Lift Coefficient (Bottom Right) ---
frame_lift = page.add_frame()
frame_lift.position = (4.7, 0.5)
frame_lift.width = 3.8
frame_lift.height = 2
plot_lift = frame_lift.plot(PlotType.XYLine)
plot_lift.activate()

ds_lift = frame_lift.create_dataset('Lift Data', ['Time', 'Cl'])
zone_lift = ds_lift.add_ordered_zone('LiftHistory', len(df))
zone_lift.values('Time')[:] = df['Time'].values
zone_lift.values('Cl')[:] = df['Cl'].values

linemap_lift = plot_lift.linemap(0)
linemap_lift.show = True
linemap_lift.zone = zone_lift
linemap_lift.line.color = Color.Red
linemap_lift.line.line_thickness = 0.4
plot_lift.axes.x_axis.title.text = 'Time (s)'
plot_lift.axes.y_axis.title.text = 'Cl'
plot_lift.view.fit()

# ==============================================================================
# 4. HELPER FUNCTIONS
# ==============================================================================

def configure_contour(variable_name, min_val, max_val, num_levels=21):
    """Configures the contour plot with specific levels and journal styling."""
    frame_flow.activate()
    plot = frame_flow.plot()
    
    # Select Variable
    try:
        var = dataset.variable(variable_name)
    except:
        print(f"Variable {variable_name} not found. Using Index 0.")
        var = dataset.variable(0)
        
    plot.contour(0).variable = var
    plot.contour(0).colormap_name = 'Sequential - Viridis' # Scientific standard
    
    # 21 Levels
    plot.contour(0).levels.reset_to_nice(min_val, max_val, num_levels)
    
    # Style: Filled + Lines
    plot.contour(0).contour_type = ContourType.FloodAndLines
    plot.contour(0).line_color = Color.Black
    plot.contour(0).line_thickness = 0.1
    
    # Legend
    plot.contour(0).legend.show = True
    plot.contour(0).legend.vertical = False
    plot.contour(0).legend.position = (5, 85) # Top inside
    plot.contour(0).legend.box.box_type = TextBox.None_

def add_streamlines():
    """Adds streamlines with arrows."""
    frame_flow.activate()
    plot = frame_flow.plot()
    plot.show_streamtraces = True
    
    st = plot.streamtraces
    st.show_arrows = True
    st.arrowhead_style = ArrowheadStyle.Filled
    st.arrowhead_size = 2.0
    
    # Place a rake of streamlines upstream (assuming flow from left -X)
    st.add_rake(start_position=(-1, -2, 0), end_position=(-1, 2, 0), stream_type=Streamtrace.TwoDLine)
    st.color = Color.Black
    st.line_thickness = 0.15

def highlight_vortex_cores():
    """Visualize vortex centers using Q-Criterion iso-lines."""
    frame_flow.activate()
    plot = frame_flow.plot()
    
    # We use a second contour group for the Vortex Cores (Q > 0)
    plot.contour(1).variable = dataset.variable('Q_Criterion')
    plot.contour(1).colormap_name = 'Diverging - Blue-Red'
    
    # Show only positive high Q values (Vortex Cores)
    plot.contour(1).levels.reset_levels([10, 50, 100, 500]) # Adjust based on scale
    plot.contour(1).legend.show = False
    
    # Overlay as thick lines
    plot.contour(1).contour_type = ContourType.Lines
    plot.contour(1).line_thickness = 0.4
    plot.show_contour = True # Ensure main switch is on

def update_time_marker(sim_time):
    """Updates a vertical line on the Drag/Lift plots to show current time."""
    for frame, plot in [(frame_drag, plot_drag), (frame_lift, plot_lift)]:
        frame.activate()
        tp.macro.execute_command(f'''
            $!ATTACHGEOM 
            GEOMTYPE = LINESEG
            RAWDATA = 2
            {sim_time} {plot.axes.y_axis.min}
            {sim_time} {plot.axes.y_axis.max}
            COLOR = BLACK
            LINEPATTERN = DASHED
        ''')

# ==============================================================================
# 5. MAIN PROCESSING LOOP
# ==============================================================================

# Get list of solution times available in dataset
solution_times = [z.solution_time for z in dataset.zones()]
target_times = np.arange(START_TIME, END_TIME + 1, TIME_STEP)

print("Starting render loop...")

for t_val in target_times:
    print(f"Processing Time: {t_val}s")
    
    # Find closest solution time index
    # (In a transient loader, we usually just set plot.solution_time)
    frame_flow.activate()
    frame_flow.plot().solution_time = t_val
    
    # Clear old geometries (time markers)
    tp.macro.execute_command('$!RemoveGeometries')
    update_time_marker(t_val)
    
    # --- Task 3 & 6: Basic Contours Animations ---
    for config in ANIMATION_VARS:
        frame_flow.activate()
        plot = frame_flow.plot()
        plot.show_streamtraces = False # Ensure streamlines off for this part
        
        configure_contour(config['var_name'], config['min'], config['max'])
        
        # Find Vortex Cores (Task 5) - Overlaying Q Criterion
        # We overlay Q-crit simply as a visual check for cores
        # (For strictly finding XYZ centers, we would extract data, but visual is standard for plots)
        highlight_vortex_cores() 

        # Export
        fname = f"{OUTPUT_DIR}/Flow_{config['name']}_t{t_val:.1f}.png"
        tp.export.save_png(fname, width=2048, supersample=3)

    # --- Task 4: Streamlines Overlay (Vorticity Background) ---
    # Specific case: Vorticity Magnitude background + Streamlines
    configure_contour('Magnitude Vorticity', 0, 1)
    add_streamlines()
    
    fname = f"{OUTPUT_DIR}/Streamlines_VortMag_t{t_val:.1f}.png"
    tp.export.save_png(fname, width=2048, supersample=3)
    
    # Specific case: Vorticity Z background + Streamlines
    configure_contour('VorticityZ', -1, 1)
    add_streamlines()
    
    fname = f"{OUTPUT_DIR}/Streamlines_VortZ_t{t_val:.1f}.png"
    tp.export.save_png(fname, width=2048, supersample=3)

print("Processing Complete. Images saved to /frames directory.")


"""
Explanation of Key Features

    Scientific Quality Layout:

        The script creates a standard "paper style" layout with the main flow field at the top and the quantitative monitoring plots (Drag/Lift coefficients) at the bottom.

        supersample=3 in the export settings ensures high DPI (300+) rendering for clean lines and text.

        A discrete colormap with 21 levels is generated using reset_to_nice.

    OpenFOAM Integration:

        It uses tp.data.load_openfoam which natively handles the polyMesh structure.

        It manually reads the forceCoeffs dat file using Pandas, which is much faster and more reliable than trying to parse text files within Tecplot macro language.

    Vortex Identification:

        Calculation: It computes the Q-Criterion using Tecplot's equation engine (QCriterion({U})). This is the standard method for identifying vortex cores (regions where rotation dominates strain).

        Visualization: It sets up a secondary contour group (plot.contour(1)) to overlay the Q-criterion iso-lines on top of the primary flow variable. This visualizes exactly where the vortex cores are located.

    Time Synchronization:

        The loop iterates through the requested time range (700s - 800s).

        update_time_marker dynamically draws a vertical dashed line on the Drag/Lift plots corresponding to the current flow field time, allowing the viewer to correlate flow structures (like vortex shedding) with force peaks.

    Streamlines:

        A "rake" (line of starting points) is defined upstream (-1, -2, 0) to (-1, 2, 0) to generate streamlines that pass over the cylinder.

        Vector arrows are enabled on the streamlines to show flow direction.
"""