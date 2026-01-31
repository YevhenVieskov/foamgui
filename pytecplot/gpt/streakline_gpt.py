#BASE SETUP
import tecplot as tp
from tecplot.constant import *
import numpy as np

tp.session.connect()
frame = tp.active_frame()

#LOAD OPENFOAM DATA (UNSTEADY)
dataset = tp.data.load_openfoam(
    case_path='.',
    read_internal_mesh=True,
    read_boundary_patches=True,
    time_values=list(range(700, 801)),
    assign_solution_time=True,
    assign_strand_ids=True
)

#EXTRACT XY PLANE
slice_zone = tp.data.extract.extract_slice(
    origin=(0, 0, 0),
    normal=(0, 0, 1),
    source=ExtractSource.VolumeZones,
    copy_cell_centered_values=True
)

#ACTIVATE 2D CARTESIAN PLOT
plot = frame.plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = False
plot.show_mesh = False

#STREAMLINES (INSTANTANEOUS)
plot.show_streamtraces = True
st = plot.streamtraces

st.streamtrace_type = StreamtraceType.VolumeLine
st.vector.u_variable = dataset.variable('U')
st.vector.v_variable = dataset.variable('V')
st.vector.w_variable = dataset.variable('W')

st.direction = StreamtraceDirection.Both
st.show_arrows = True
st.arrowhead_spacing = 5

# Seed points upstream of cylinder
for y in np.linspace(-1.0, 1.0, 15):
    st.add(seed_point=(-2.0, y, 0.0))

#PATHLINES (PARTICLE TRAJECTORIES)	
plot.show_pathlines = True
pl = plot.pathlines

pl.release_time = 700.0
pl.stop_time = 800.0
pl.time_step = 0.5

pl.vector.u_variable = dataset.variable('U')
pl.vector.v_variable = dataset.variable('V')
pl.vector.w_variable = dataset.variable('W')

pl.show_arrows = True
pl.arrowhead_spacing = 8

# Initial particle locations
for y in np.linspace(-0.8, 0.8, 10):
    pl.add_seed(seed_point=(-2.0, y, 0.0))

#STREAKLINES (CONTINUOUS PARTICLE RELEASE)	
plot.show_streaklines = True
sl = plot.streaklines

sl.release_start_time = 700.0
sl.release_stop_time = 800.0
sl.release_interval = 0.5

sl.stop_time = 800.0
sl.time_step = 0.5

sl.vector.u_variable = dataset.variable('U')
sl.vector.v_variable = dataset.variable('V')
sl.vector.w_variable = dataset.variable('W')

sl.show_arrows = True
sl.arrowhead_spacing = 10

# Fixed release points
for y in np.linspace(-0.5, 0.5, 6):
    sl.add_release_point((-0.5, y, 0.0))
	
#VISUAL QUALITY (JOURNAL)	
plot.axes.x_axis.title.text = r'$x/D$'
plot.axes.y_axis.title.text = r'$y/D$'

plot.view.fit()

plot.streamtraces.coloring.variable = dataset.variable('Vorticity_Z')
plot.streamtraces.coloring.colormap = tp.color_maps['Viridis']

#EXPORT FIGURES
tp.export.save_png(
    'figures/lines_comparison.png',
    width=2000,
    supersample=3
)

tp.export.save_pdf(
    'figures/lines_comparison.pdf'
)
