import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
import numpy as np
import pandas as pd
import os

tp.session.connect()

dataset = tp.data.load_openfoam(
    case_path='.',
    read_internal_mesh=True,
    read_boundary_patches=True,
    time_values=list(range(700, 801)),
    assign_solution_time=True,
    assign_strand_ids=True
)

slice_zone = tp.data.extract.extract_slice(
    origin=(0, 0, 0),
    normal=(0, 0, 1),
    source=ExtractSource.VolumeZones,
    copy_cell_centered_values=True
)


tp.data.operate.execute_equation(
    '{Umag} = sqrt({U}**2 + {V}**2)'
)

tp.macro.execute_command("""
$!ExtendedCommand
  CommandProcessorID='CFDAnalyzer4'
  Command='Calculate Function=Vorticity Normalization=None'
""")

tp.macro.execute_command("""
$!ExtendedCommand
  CommandProcessorID='CFDAnalyzer4'
  Command='Calculate Function=VorticityMagnitude Normalization=None'
""")

tp.macro.execute_command("""
$!ExtendedCommand
  CommandProcessorID='CFDAnalyzer4'
  Command='Calculate Function=QCriterion Normalization=None'
""")

def setup_contour(varname, vmin=None, vmax=None):
    plot = tp.active_frame().plot()
    contour = plot.contour(0)
    contour.variable = dataset.variable(varname)
    contour.colormap = cmap
    contour.levels.reset_to_nice(21)
    if vmin is not None:
        contour.levels.min = vmin
        contour.levels.max = vmax
    contour.flood_contour = True
    contour.line_contour = True

	
plot = tp.active_frame().plot(PlotType.Cartesian2D)
plot.show_streamtraces = True

st = plot.streamtraces
st.add(seed_point=(0.5, 0.0, 0.0))
st.direction = StreamtraceDirection.Both
st.show_arrows = True
st.arrowhead_spacing = 5

#Q-criterion + critical points
tp.macro.execute_command("""
$!ExtendedCommand
  CommandProcessorID='CFDAnalyzer4'
  Command='Find Critical Points Variable=QCriterion Type=Vortex'
""")

#Extract vortex centers for tracking
vortex_centers = []

for zone in dataset.zones():
    if 'CriticalPoints' in zone.name:
        x = zone.values('X')[:]
        y = zone.values('Y')[:]
        t = zone.solution_time
        for xi, yi in zip(x, y):
            vortex_centers.append([t, xi, yi])

vortex_df = pd.DataFrame(vortex_centers, columns=['time','x','y'])
vortex_df.to_csv('figures/vortex_centers.csv', index=False)

# LOAD forceCoeffs.dat (DRAG & LIFT)
fc = pd.read_csv(
    'postProcessing/forceCoeffs/0/forceCoeffs.dat',
    delim_whitespace=True,
    comment='#',
    names=['time','Cd','Cl','Cm']
)

fc = fc[(fc.time >= 700) & (fc.time <= 800)]

#MULTI-VIEWPORT LAYOUT
frame = tp.active_frame()

# Flow visualization
vp_flow = frame.add_viewport((0.02, 0.05, 0.68, 0.95))

# Force coefficients
vp_force = frame.add_viewport((0.72, 0.55, 0.98, 0.95))

#DRAG & LIFT PLOTS
frame.activate_viewport(vp_force)
plot = frame.plot(PlotType.XYLine)

plot.activate()

plot.add_xy_line(fc.time, fc.Cl, line_thickness=2)
plot.add_xy_line(fc.time, fc.Cd, line_thickness=2)

plot.legend.show = True
plot.axes.x_axis.title.text = r'$t$'
plot.axes.y_axis.title.text = r'$C_L,\;C_D$'

#LaTeX-READY FIGURE EXPORT
tp.export.save_png(
    'figures/vorticity.png',
    width=1800,
    supersample=3
)

tp.export.save_pdf(
    'figures/vorticity.pdf'
)

#ANIMATION EXPORT
tp.export.save_avi(
    'animations/cylinder_vorticity.avi',
    start_time=700,
    end_time=800,
    delta_time=1,
    width=1920,
    frame_rate=20
)
