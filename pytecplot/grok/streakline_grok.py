import tecplot as tp
from tecplot.constant import *
import tecplot.macro as macro  # for executing extended commands

# Connect to Tecplot 360 if not already (optional, often run from inside Tecplot)
# tp.session.connect()

# Assume dataset is already loaded (e.g., OpenFOAM case with unsteady data)
# If needed: tp.data.load_tecplot('your_data.plt') or load_openfoam(...)
dataset = tp.active_dataset()
print(f"Dataset has {len(dataset.solution_times)} time steps.")

# Set velocity components for streamtraces / particle integration
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'SetVelocityComponents XComponent = "U[X]" YComponent = "U[Y]" ZComponent = "U[Z]"'
''')

# ========================
# 1. STREAMLINES (instantaneous streamtraces)
# ========================
frame = tp.active_frame()
plot = frame.plot()
plot.plot_type = PlotType.Cartesian3D  # or Cartesian2D for 2D slice

# Enable and configure streamtraces
plot.show_streamtraces = True
streamtraces = plot.streamtraces

# Clear any existing
streamtraces.clear()

# Example: Add streamlines as lines (adjust style: lines, ribbons, rods)
streamtraces.line_color = Color.Black
streamtraces.line_thickness = 0.6
streamtraces.arrowhead.show = True
streamtraces.arrowhead.size = 3.0

# Seed example: rake of points upstream of cylinder (adjust coordinates!)
# Assume cylinder at origin, inlet at x = -10, domain in XY plane
seed_points = [
    (-10.0,  y, 0.0) for y in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
]  # CHANGE to your inlet/freestream location

# Add streamtraces from list of points (forward + backward integration)
streamtraces.add_streamtraces(
    tp.data.PointSet(seed_points),
    stream_type=Streamtraces.VolumeLine,  # alternatives: VolumeRibbon, VolumeRod, SurfaceLine
    direction=StreamDirection.ForwardAndBackward
)

# Optional: add more rakes (e.g., near wake)
# streamtraces.add_streamtraces(...)

tp.redraw()
print("Streamlines created.")

# ========================
# 2. STREAKLINES (particles released continuously at fixed points over time)
# ========================
# Use Particle Paths with multiple releases per time step
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'ParticlePathOptions ReleaseParticlesPerSolutionTime = 3 IntegrationTimeStep = 0.01 NumParticlesToRelease = 100'  # adjust params
''')

# Define release (seed) points - same as rake above, but fixed in space
# Particles released at these points every time step
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'ResetParticleSeeds'
''')

for pt in seed_points:
    macro.execute_command(f'''
        $!EXTENDEDCOMMAND 
          COMMANDPROCESSORID = 'CFDAnalyzer4'
          COMMAND = 'AddParticleSeed X={pt[0]} Y={pt[1]} Z={pt[2]}'
    ''')

# Calculate streaklines (integrate all released particles over time)
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'CalculateStreaklines'
''')

tp.redraw()
print("Streaklines calculated and added as new zone(s). Enable scatter or lines on streakline zones in Zone Style.")

# ========================
# 3. PATHLINES (particle paths - trajectory of individual particles released at specific time)
# ========================
# Example: release particles at t=700s and integrate forward
plot.solution_time = 700.0  # starting time for pathlines

# Reset seeds if needed
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'ResetParticleSeeds'
''')

# Add seeds (can be single or multiple points)
for pt in seed_points[:3]:  # example: fewer for pathlines
    macro.execute_command(f'''
        $!EXTENDEDCOMMAND 
          COMMANDPROCESSORID = 'CFDAnalyzer4'
          COMMAND = 'AddParticleSeed X={pt[0]} Y={pt[1]} Z={pt[2]}'
    ''')

# Calculate particle paths
macro.execute_command(r'''
    $!EXTENDEDCOMMAND 
      COMMANDPROCESSORID = 'CFDAnalyzer4'
      COMMAND = 'CalculateParticlePaths'
''')

tp.redraw()
print("Pathlines calculated and added as new zone(s). Style as scatter/line in Zone Style.")

# ========================
# Visualization & Animation Tips
# ========================
# - For streaklines/pathlines: in sidebar -> Zone Style, show only streakline/pathline zones, enable Scatter or Line, color by time or velocity.
# - To animate: use time slider or animate over solution times (streamtraces update instantly; streak/path zones show history).
# - Extract streamtraces to zones for further analysis/export:
#   tp.data.extract.streamtraces(extract_blanked=False)
# - Journal quality: add legends, adjust fonts, export high-res PNGs or MP4 animation.

tp.save_layout('flow_lines_visualization.lay')
print("Layout saved. Adjust zones, colors, and animate in Tecplot 360.")

"""
Streamlines: Instant snapshot at current time; reintegrate every time step (dynamic in animation).
Streaklines: Continuous release at fixed spatial points > shows "dye streak" effect over time.
Pathlines: Single release at specific time > tracks where each particle goes (true Lagrangian paths).
"""