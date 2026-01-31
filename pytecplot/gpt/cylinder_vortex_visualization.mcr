#!MC 1410
$!MacroFunction Name = "Cylinder_OGrid_Visualization"

# ============================================================
# 1. LOAD OPENFOAM CASE
# ============================================================

$!ReadDataSet  \
  'STANDARDSYNTAX' \
  DataSetReader = 'OpenFOAM Loader' \
  ReadTimeMode = ByList \
  TimeValueList = '700-800:1' \
  AssignStrandIDs = Yes \
  AssignSolutionTime = Yes \
  CasePath = './' \
  ReadInternalMesh = Yes \
  ReadBoundaryPatches = Yes

$!RedrawAll

# ============================================================
# 2. CREATE XY-PLANE SECTION
# ============================================================

$!SliceAttributes 1
  SliceSurface = ZPlanes
  PrimaryPosition { Z = 0.0 }
  ShowPrimarySlice = Yes
  ExtractMode = SingleZone
  SliceSource = VolumeZones

$!CreateSlice

# ============================================================
# 3. DERIVED VARIABLES
# ============================================================

# Velocity magnitude
$!ExtendedCommand
  CommandProcessorID = 'CFDAnalyzer4'
  Command = '
    Calculate Function = VelocityMagnitude
    Normalization = None
  '

# Vorticity vector
$!ExtendedCommand
  CommandProcessorID = 'CFDAnalyzer4'
  Command = '
    Calculate Function = Vorticity
    Normalization = None
  '

# Vorticity magnitude
$!ExtendedCommand
  CommandProcessorID = 'CFDAnalyzer4'
  Command = '
    Calculate Function = VorticityMagnitude
    Normalization = None
  '

# ============================================================
# 4. COLORMAP (21 COLORS)
# ============================================================

$!CreateColorMap
  Name = 'Journal21'
  NumLevels = 21
  ColorMapType = Continuous

$!SetContourVar
  Var = 1

# ============================================================
# 5. FILLED CONTOURS + LINES
# ============================================================

# ---------- PRESSURE ----------
$!ContourAttributes
  Var = 'p'
  ColorMapName = 'Journal21'
  ContourType = LinesAndFlood
  NumLevels = 21

# ---------- VELOCITY MAG ----------
$!ContourAttributes
  Var = 'VelocityMagnitude'
  ColorMapName = 'Journal21'
  ContourType = LinesAndFlood
  NumLevels = 21

# ---------- VORTICITY ----------
$!ContourAttributes
  Var = 'Vorticity_Z'
  ColorMapName = 'Journal21'
  ContourType = LinesAndFlood
  MinLevel = -1
  MaxLevel =  1
  NumLevels = 21

# ---------- VORTICITY MAG ----------
$!ContourAttributes
  Var = 'VorticityMagnitude'
  ColorMapName = 'Journal21'
  ContourType = LinesAndFlood
  MinLevel = 0
  MaxLevel = 1
  NumLevels = 21

# ============================================================
# 6. STREAMLINES WITH VECTOR ARROWS
# ============================================================

$!StreamtraceAttributes
  StreamtraceType = VolumeLine
  Direction = Both
  VectorVariable { U = 'U' V = 'V' W = 'W' }
  ShowArrowheads = Yes
  ArrowheadSpacing = 5
  MaxSteps = 5000

$!CreateStreamtrace

# ============================================================
# 7. VORTEX CORE DETECTION
# ============================================================

# Q-criterion
$!ExtendedCommand
  CommandProcessorID = 'CFDAnalyzer4'
  Command = '
    Calculate Function = QCriterion
    Normalization = None
  '

# Critical points (vortex centers)
$!ExtendedCommand
  CommandProcessorID = 'CFDAnalyzer4'
  Command = '
    Find Critical Points
    Variable = VelocityMagnitude
    Type = Vortex
  '

# ============================================================
# 8. MULTI-VIEWPORT LAYOUT
# ============================================================

# Main flow visualization
$!CreateViewport
  Left = 5
  Right = 70
  Top = 95
  Bottom = 5

# Drag/Lift viewport
$!CreateViewport
  Left = 72
  Right = 98
  Top = 95
  Bottom = 55

# Force coefficients
$!XYLinePlot
  XVar = 'Time'
  YVar = 'Cl'

$!XYLinePlot
  XVar = 'Time'
  YVar = 'Cd'

$!Legend
  Show = Yes
  TextFont { Size = 14 }

# ============================================================
# 9. ANIMATION EXPORT
# ============================================================

$!Animate
  StartTime = 700
  EndTime = 800
  DeltaTime = 1

$!ExportSetup
  ExportFormat = AVI
  ExportFileName = 'cylinder_vortex.avi'
  ImageWidth = 1920
  ImageHeight = 1080
  FrameRate = 20

$!Export
  ExportRegion = AllFrames

$!RedrawAll
