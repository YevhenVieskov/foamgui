# state file generated using paraview version 5.11.2
import paraview
paraview.compatibility.major = 5
paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [1343, 773]
renderView1.InteractionMode = '2D'
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [0.0, 0.0, 43.19751617610021]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 11.180339887498937
renderView1.CameraParallelProjection = 1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(1343, 773)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'CSV Reader'
p_Final_txtcsv = CSVReader(registrationName='P_Final_txt.csv', FileName=['/home/yevhenv/OpenFOAM/moving_domain/paraview/P_Final_txt.csv'])

# create a new 'Table To Points'
tableToPoints1 = TableToPoints(registrationName='TableToPoints1', Input=p_Final_txtcsv)
tableToPoints1.XColumn = '1'
tableToPoints1.YColumn = '2'
tableToPoints1.ZColumn = '3'

# create a new 'OpenFOAMReader'
casefoam = OpenFOAMReader(registrationName='case.foam', FileName='/home/yevhenv/OpenFOAM/moving_domain/cylinder/article1/cylinderRe200linearUpvindV/case.foam')
casefoam.MeshRegions = ['internalMesh']
casefoam.CellArrays = ['LambVectorField', 'Lambda2Field', 'Q', 'U', 'V0', 'mag(wallShearStress)', 'p', 'staticCoeffP', 'staticP', 'totalCoeffP', 'totalP', 'turbulenceProperties:R', 'vorticity', 'wallShearStress', 'yPlus']

# create a new 'Temporal Interpolator'
temporalInterpolator1 = TemporalInterpolator(registrationName='TemporalInterpolator1', Input=casefoam)
temporalInterpolator1.ResampleFactor = 20

# create a new 'Slice'
slice1 = Slice(registrationName='Slice1', Input=temporalInterpolator1)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# create a new 'Calculator'
calculatorVelocity = Calculator(registrationName='CalculatorVelocity', Input=slice1)
calculatorVelocity.ResultArrayName = 'Velocity'
calculatorVelocity.Function = 'U_X*iHat+U_Y*jHat+U_Z*kHat'

# create a new 'StreakLine'
streakLine1 = StreakLine(registrationName='StreakLine1', Input=calculatorVelocity,
    SeedSource=tableToPoints1)
streakLine1.TerminationTime = 400.0
streakLine1.SelectInputVectors = ['POINTS', 'Velocity']

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from casefoam
casefoamDisplay = Show(casefoam, renderView1, 'UnstructuredGridRepresentation')

# get 2D transfer function for 'yPlus'
yPlusTF2D = GetTransferFunction2D('yPlus')

# get color transfer function/color map for 'yPlus'
yPlusLUT = GetColorTransferFunction('yPlus')
yPlusLUT.AutomaticRescaleRangeMode = 'Never'
yPlusLUT.TransferFunction2D = yPlusTF2D
yPlusLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 0.2362416386604309, 1.0, 0.0, 0.0]
yPlusLUT.ColorSpace = 'HSV'
yPlusLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
yPlusLUT.NumberOfTableValues = 21
yPlusLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'yPlus'
yPlusPWF = GetOpacityTransferFunction('yPlus')
yPlusPWF.Points = [0.0, 0.0, 0.5, 0.0, 0.2362416386604309, 1.0, 0.5, 0.0]
yPlusPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
casefoamDisplay.Representation = 'Surface'
casefoamDisplay.ColorArrayName = ['POINTS', 'yPlus']
casefoamDisplay.LookupTable = yPlusLUT
casefoamDisplay.SelectTCoordArray = 'None'
casefoamDisplay.SelectNormalArray = 'None'
casefoamDisplay.SelectTangentArray = 'None'
casefoamDisplay.OSPRayScaleArray = 'p'
casefoamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
casefoamDisplay.SelectOrientationVectors = 'U'
casefoamDisplay.ScaleFactor = 10.0
casefoamDisplay.SelectScaleArray = 'p'
casefoamDisplay.GlyphType = 'Arrow'
casefoamDisplay.GlyphTableIndexArray = 'p'
casefoamDisplay.GaussianRadius = 0.5
casefoamDisplay.SetScaleArray = ['POINTS', 'p']
casefoamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
casefoamDisplay.OpacityArray = ['POINTS', 'p']
casefoamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
casefoamDisplay.DataAxesGrid = 'GridAxesRepresentation'
casefoamDisplay.PolarAxes = 'PolarAxesRepresentation'
casefoamDisplay.ScalarOpacityFunction = yPlusPWF
casefoamDisplay.ScalarOpacityUnitDistance = 4.551474389381354
casefoamDisplay.OpacityArrayName = ['POINTS', 'p']
casefoamDisplay.SelectInputVectors = ['POINTS', 'U']
casefoamDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
casefoamDisplay.ScaleTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
casefoamDisplay.OpacityTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# show data from temporalInterpolator1
temporalInterpolator1Display = Show(temporalInterpolator1, renderView1, 'UnstructuredGridRepresentation')

# get 2D transfer function for 'U'
uTF2D = GetTransferFunction2D('U')

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
uLUT.AutomaticRescaleRangeMode = 'Never'
uLUT.TransferFunction2D = uTF2D
uLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 1.448959426265538, 1.0, 0.0, 0.0]
uLUT.ColorSpace = 'HSV'
uLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
uLUT.NumberOfTableValues = 21
uLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.448959426265538, 1.0, 0.5, 0.0]
uPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
temporalInterpolator1Display.Representation = 'Surface'
temporalInterpolator1Display.ColorArrayName = ['POINTS', 'U']
temporalInterpolator1Display.LookupTable = uLUT
temporalInterpolator1Display.SelectTCoordArray = 'None'
temporalInterpolator1Display.SelectNormalArray = 'None'
temporalInterpolator1Display.SelectTangentArray = 'None'
temporalInterpolator1Display.OSPRayScaleArray = 'p'
temporalInterpolator1Display.OSPRayScaleFunction = 'PiecewiseFunction'
temporalInterpolator1Display.SelectOrientationVectors = 'U'
temporalInterpolator1Display.ScaleFactor = 10.0
temporalInterpolator1Display.SelectScaleArray = 'p'
temporalInterpolator1Display.GlyphType = 'Arrow'
temporalInterpolator1Display.GlyphTableIndexArray = 'p'
temporalInterpolator1Display.GaussianRadius = 0.5
temporalInterpolator1Display.SetScaleArray = ['POINTS', 'p']
temporalInterpolator1Display.ScaleTransferFunction = 'PiecewiseFunction'
temporalInterpolator1Display.OpacityArray = ['POINTS', 'p']
temporalInterpolator1Display.OpacityTransferFunction = 'PiecewiseFunction'
temporalInterpolator1Display.DataAxesGrid = 'GridAxesRepresentation'
temporalInterpolator1Display.PolarAxes = 'PolarAxesRepresentation'
temporalInterpolator1Display.ScalarOpacityFunction = uPWF
temporalInterpolator1Display.ScalarOpacityUnitDistance = 4.551474389381354
temporalInterpolator1Display.OpacityArrayName = ['POINTS', 'p']
temporalInterpolator1Display.SelectInputVectors = ['POINTS', 'U']
temporalInterpolator1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
temporalInterpolator1Display.ScaleTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
temporalInterpolator1Display.OpacityTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# show data from slice1
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

# get 2D transfer function for 'vorticity'
vorticityTF2D = GetTransferFunction2D('vorticity')
vorticityTF2D.ScalarRangeInitialized = 1
vorticityTF2D.Range = [-1.0, 1.0, 0.0, 1.0]

# get color transfer function/color map for 'vorticity'
vorticityLUT = GetColorTransferFunction('vorticity')
vorticityLUT.AutomaticRescaleRangeMode = 'Never'
vorticityLUT.TransferFunction2D = vorticityTF2D
vorticityLUT.RGBPoints = [-1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]
vorticityLUT.ColorSpace = 'HSV'
vorticityLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
vorticityLUT.NumberOfTableValues = 21
vorticityLUT.ScalarRangeInitialized = 1.0
vorticityLUT.VectorComponent = 2
vorticityLUT.VectorMode = 'Component'

# trace defaults for the display properties.
slice1Display.Representation = 'Surface'
slice1Display.ColorArrayName = ['POINTS', 'vorticity']
slice1Display.LookupTable = vorticityLUT
slice1Display.SelectTCoordArray = 'None'
slice1Display.SelectNormalArray = 'None'
slice1Display.SelectTangentArray = 'None'
slice1Display.OSPRayScaleArray = 'p'
slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice1Display.SelectOrientationVectors = 'U'
slice1Display.ScaleFactor = 10.0
slice1Display.SelectScaleArray = 'p'
slice1Display.GlyphType = 'Arrow'
slice1Display.GlyphTableIndexArray = 'p'
slice1Display.GaussianRadius = 0.5
slice1Display.SetScaleArray = ['POINTS', 'p']
slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice1Display.OpacityArray = ['POINTS', 'p']
slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice1Display.DataAxesGrid = 'GridAxesRepresentation'
slice1Display.PolarAxes = 'PolarAxesRepresentation'
slice1Display.SelectInputVectors = ['POINTS', 'U']
slice1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice1Display.ScaleTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice1Display.OpacityTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# show data from calculatorVelocity
calculatorVelocityDisplay = Show(calculatorVelocity, renderView1, 'GeometryRepresentation')

# get 2D transfer function for 'Velocity'
velocityTF2D = GetTransferFunction2D('Velocity')

# get color transfer function/color map for 'Velocity'
velocityLUT = GetColorTransferFunction('Velocity')
velocityLUT.TransferFunction2D = velocityTF2D
velocityLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 1.4313095515380458, 1.0, 0.0, 0.0]
velocityLUT.ColorSpace = 'HSV'
velocityLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
velocityLUT.NumberOfTableValues = 21
velocityLUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
calculatorVelocityDisplay.Representation = 'Surface'
calculatorVelocityDisplay.ColorArrayName = ['POINTS', 'Velocity']
calculatorVelocityDisplay.LookupTable = velocityLUT
calculatorVelocityDisplay.SelectTCoordArray = 'None'
calculatorVelocityDisplay.SelectNormalArray = 'None'
calculatorVelocityDisplay.SelectTangentArray = 'None'
calculatorVelocityDisplay.OSPRayScaleArray = 'p'
calculatorVelocityDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculatorVelocityDisplay.SelectOrientationVectors = 'Velocity'
calculatorVelocityDisplay.ScaleFactor = 10.0
calculatorVelocityDisplay.SelectScaleArray = 'p'
calculatorVelocityDisplay.GlyphType = 'Arrow'
calculatorVelocityDisplay.GlyphTableIndexArray = 'p'
calculatorVelocityDisplay.GaussianRadius = 0.5
calculatorVelocityDisplay.SetScaleArray = ['POINTS', 'p']
calculatorVelocityDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculatorVelocityDisplay.OpacityArray = ['POINTS', 'p']
calculatorVelocityDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculatorVelocityDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculatorVelocityDisplay.PolarAxes = 'PolarAxesRepresentation'
calculatorVelocityDisplay.SelectInputVectors = ['POINTS', 'Velocity']
calculatorVelocityDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculatorVelocityDisplay.ScaleTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculatorVelocityDisplay.OpacityTransferFunction.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]

# show data from tableToPoints1
tableToPoints1Display = Show(tableToPoints1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
tableToPoints1Display.Representation = 'Points'
tableToPoints1Display.AmbientColor = [0.0, 0.0, 0.0]
tableToPoints1Display.ColorArrayName = [None, '']
tableToPoints1Display.DiffuseColor = [0.0, 0.0, 0.0]
tableToPoints1Display.SelectTCoordArray = 'None'
tableToPoints1Display.SelectNormalArray = 'None'
tableToPoints1Display.SelectTangentArray = 'None'
tableToPoints1Display.OSPRayScaleFunction = 'PiecewiseFunction'
tableToPoints1Display.SelectOrientationVectors = 'None'
tableToPoints1Display.ScaleFactor = 0.020000000000000004
tableToPoints1Display.SelectScaleArray = 'None'
tableToPoints1Display.GlyphType = 'Arrow'
tableToPoints1Display.GlyphTableIndexArray = 'None'
tableToPoints1Display.GaussianRadius = 0.001
tableToPoints1Display.SetScaleArray = [None, '']
tableToPoints1Display.ScaleTransferFunction = 'PiecewiseFunction'
tableToPoints1Display.OpacityArray = [None, '']
tableToPoints1Display.OpacityTransferFunction = 'PiecewiseFunction'
tableToPoints1Display.DataAxesGrid = 'GridAxesRepresentation'
tableToPoints1Display.PolarAxes = 'PolarAxesRepresentation'
tableToPoints1Display.SelectInputVectors = [None, '']
tableToPoints1Display.WriteLog = ''

# show data from streakLine1
streakLine1Display = Show(streakLine1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
streakLine1Display.Representation = 'Surface'
streakLine1Display.ColorArrayName = ['POINTS', 'U']
streakLine1Display.LookupTable = uLUT
streakLine1Display.RenderLinesAsTubes = 1
streakLine1Display.SelectTCoordArray = 'None'
streakLine1Display.SelectNormalArray = 'None'
streakLine1Display.SelectTangentArray = 'None'
streakLine1Display.OSPRayScaleArray = 'p'
streakLine1Display.OSPRayScaleFunction = 'PiecewiseFunction'
streakLine1Display.SelectOrientationVectors = 'Velocity'
streakLine1Display.ScaleFactor = 2.002532958984375
streakLine1Display.SelectScaleArray = 'p'
streakLine1Display.GlyphType = 'Arrow'
streakLine1Display.GlyphTableIndexArray = 'p'
streakLine1Display.GaussianRadius = 0.10012664794921876
streakLine1Display.SetScaleArray = ['POINTS', 'p']
streakLine1Display.ScaleTransferFunction = 'PiecewiseFunction'
streakLine1Display.OpacityArray = ['POINTS', 'p']
streakLine1Display.OpacityTransferFunction = 'PiecewiseFunction'
streakLine1Display.DataAxesGrid = 'GridAxesRepresentation'
streakLine1Display.PolarAxes = 'PolarAxesRepresentation'
streakLine1Display.SelectInputVectors = ['POINTS', 'Velocity']
streakLine1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
streakLine1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.448959426265538, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
streakLine1Display.ScaleTransferFunction.Points = [-0.8129453063011169, 0.0, 0.5, 0.0, 0.4917713701725006, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
streakLine1Display.OpacityTransferFunction.Points = [-0.8129453063011169, 0.0, 0.5, 0.0, 0.4917713701725006, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D('p')

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')
pLUT.AutomaticRescaleRangeMode = 'Never'
pLUT.TransferFunction2D = pTF2D
pLUT.RGBPoints = [-0.8234872817993164, 0.0, 0.0, 1.0, 0.5222266912460327, 1.0, 0.0, 0.0]
pLUT.ColorSpace = 'HSV'
pLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
pLUT.NumberOfTableValues = 21
pLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for pLUT in view renderView1
pLUTColorBar = GetScalarBar(pLUT, renderView1)
pLUTColorBar.AutoOrient = 0
pLUTColorBar.Orientation = 'Horizontal'
pLUTColorBar.WindowLocation = 'Upper Right Corner'
pLUTColorBar.Title = '$p_k = {p_s}/{\\rho}{, } \\;  \\left[ {m^2}/{s^2} \\right]$'
pLUTColorBar.ComponentTitle = ''
pLUTColorBar.HorizontalTitle = 1
pLUTColorBar.TitleFontSize = 20
pLUTColorBar.LabelFontSize = 20
pLUTColorBar.ScalarBarThickness = 24
pLUTColorBar.ScalarBarLength = 0.35
pLUTColorBar.DrawBackground = 1
pLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
pLUTColorBar.DrawScalarBarOutline = 1
pLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
pLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
pLUTColorBar.Visibility = 0

# get color legend/bar for vorticityLUT in view renderView1
vorticityLUTColorBar = GetScalarBar(vorticityLUT, renderView1)
vorticityLUTColorBar.AutoOrient = 0
vorticityLUTColorBar.Orientation = 'Horizontal'
vorticityLUTColorBar.WindowLocation = 'Upper Center'
vorticityLUTColorBar.Title = '$\\omega_Z {, } \\;  \\left[ {1}/{s} \\right]$'
vorticityLUTColorBar.ComponentTitle = ''
vorticityLUTColorBar.HorizontalTitle = 1
vorticityLUTColorBar.TitleFontSize = 20
vorticityLUTColorBar.LabelFontSize = 20
vorticityLUTColorBar.ScalarBarThickness = 24
vorticityLUTColorBar.ScalarBarLength = 0.35
vorticityLUTColorBar.DrawBackground = 1
vorticityLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
vorticityLUTColorBar.DrawScalarBarOutline = 1
vorticityLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
vorticityLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
vorticityLUTColorBar.Visibility = 0

# get 2D transfer function for 'Vorticity'
vorticityTF2D_1 = GetTransferFunction2D('Vorticity')
vorticityTF2D_1.ScalarRangeInitialized = 1

# get color transfer function/color map for 'Vorticity'
vorticityLUT_1 = GetColorTransferFunction('Vorticity')
vorticityLUT_1.AutomaticRescaleRangeMode = 'Never'
vorticityLUT_1.TransferFunction2D = vorticityTF2D_1
vorticityLUT_1.RGBPoints = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]
vorticityLUT_1.ColorSpace = 'HSV'
vorticityLUT_1.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
vorticityLUT_1.ScalarRangeInitialized = 1.0

# get color legend/bar for vorticityLUT_1 in view renderView1
vorticityLUT_1ColorBar = GetScalarBar(vorticityLUT_1, renderView1)
vorticityLUT_1ColorBar.AutoOrient = 0
vorticityLUT_1ColorBar.Orientation = 'Horizontal'
vorticityLUT_1ColorBar.WindowLocation = 'Any Location'
vorticityLUT_1ColorBar.Position = [0.4272948822095857, 0.891946957922537]
vorticityLUT_1ColorBar.Title = '$\\omega {, } \\;  \\left[ {1}/{s} \\right]$'
vorticityLUT_1ColorBar.ComponentTitle = ''
vorticityLUT_1ColorBar.HorizontalTitle = 1
vorticityLUT_1ColorBar.TitleFontSize = 20
vorticityLUT_1ColorBar.LabelFontSize = 20
vorticityLUT_1ColorBar.ScalarBarThickness = 24
vorticityLUT_1ColorBar.ScalarBarLength = 0.3499999999999998
vorticityLUT_1ColorBar.DrawBackground = 1
vorticityLUT_1ColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
vorticityLUT_1ColorBar.DrawScalarBarOutline = 1
vorticityLUT_1ColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
vorticityLUT_1ColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
vorticityLUT_1ColorBar.Visibility = 0

# get 2D transfer function for 'VorticityZ'
vorticityZTF2D = GetTransferFunction2D('VorticityZ')

# get color transfer function/color map for 'VorticityZ'
vorticityZLUT = GetColorTransferFunction('VorticityZ')
vorticityZLUT.TransferFunction2D = vorticityZTF2D
vorticityZLUT.RGBPoints = [-31.629619598388672, 0.231373, 0.298039, 0.752941, 0.2177753448486328, 0.865003, 0.865003, 0.865003, 32.06517028808594, 0.705882, 0.0156863, 0.14902]
vorticityZLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for vorticityZLUT in view renderView1
vorticityZLUTColorBar = GetScalarBar(vorticityZLUT, renderView1)
vorticityZLUTColorBar.Title = 'VorticityZ'
vorticityZLUTColorBar.ComponentTitle = ''

# set color bar visibility
vorticityZLUTColorBar.Visibility = 0

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.AutoOrient = 0
uLUTColorBar.Orientation = 'Horizontal'
uLUTColorBar.WindowLocation = 'Upper Center'
uLUTColorBar.Title = '$U {, } \\;  \\left[ {m}/{s} \\right]$'
uLUTColorBar.ComponentTitle = ''
uLUTColorBar.HorizontalTitle = 1
uLUTColorBar.TitleFontSize = 20
uLUTColorBar.LabelFontSize = 20
uLUTColorBar.ScalarBarThickness = 24
uLUTColorBar.ScalarBarLength = 0.35
uLUTColorBar.DrawBackground = 1
uLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
uLUTColorBar.DrawScalarBarOutline = 1
uLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
uLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
uLUTColorBar.Visibility = 1

# get 2D transfer function for 'LambVectorField'
lambVectorFieldTF2D = GetTransferFunction2D('LambVectorField')

# get color transfer function/color map for 'LambVectorField'
lambVectorFieldLUT = GetColorTransferFunction('LambVectorField')
lambVectorFieldLUT.AutomaticRescaleRangeMode = 'Never'
lambVectorFieldLUT.TransferFunction2D = lambVectorFieldTF2D
lambVectorFieldLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 16.98756221355132, 1.0, 0.0, 0.0]
lambVectorFieldLUT.ColorSpace = 'HSV'
lambVectorFieldLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
lambVectorFieldLUT.NumberOfTableValues = 21
lambVectorFieldLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for lambVectorFieldLUT in view renderView1
lambVectorFieldLUTColorBar = GetScalarBar(lambVectorFieldLUT, renderView1)
lambVectorFieldLUTColorBar.AutoOrient = 0
lambVectorFieldLUTColorBar.Orientation = 'Horizontal'
lambVectorFieldLUTColorBar.WindowLocation = 'Upper Center'
lambVectorFieldLUTColorBar.Position = [0.32127351664254705, 0.8958279411049432]
lambVectorFieldLUTColorBar.Title = '$l {, } \\;  \\left[ {m}/{s^2} \\right]$'
lambVectorFieldLUTColorBar.ComponentTitle = ''
lambVectorFieldLUTColorBar.HorizontalTitle = 1
lambVectorFieldLUTColorBar.TitleFontSize = 20
lambVectorFieldLUTColorBar.LabelFontSize = 20
lambVectorFieldLUTColorBar.ScalarBarThickness = 20
lambVectorFieldLUTColorBar.ScalarBarLength = 0.35
lambVectorFieldLUTColorBar.DrawBackground = 1
lambVectorFieldLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
lambVectorFieldLUTColorBar.DrawScalarBarOutline = 1
lambVectorFieldLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
lambVectorFieldLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
lambVectorFieldLUTColorBar.Visibility = 0

# get 2D transfer function for 'wallShearStress'
wallShearStressTF2D = GetTransferFunction2D('wallShearStress')

# get color transfer function/color map for 'wallShearStress'
wallShearStressLUT = GetColorTransferFunction('wallShearStress')
wallShearStressLUT.AutomaticRescaleRangeMode = 'Never'
wallShearStressLUT.TransferFunction2D = wallShearStressTF2D
wallShearStressLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 0.16981748115213044, 1.0, 0.0, 0.0]
wallShearStressLUT.ColorSpace = 'HSV'
wallShearStressLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
wallShearStressLUT.NumberOfTableValues = 21
wallShearStressLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for wallShearStressLUT in view renderView1
wallShearStressLUTColorBar = GetScalarBar(wallShearStressLUT, renderView1)
wallShearStressLUTColorBar.AutoOrient = 0
wallShearStressLUTColorBar.Orientation = 'Horizontal'
wallShearStressLUTColorBar.WindowLocation = 'Upper Center'
wallShearStressLUTColorBar.Title = '$\\tau {, } \\;  \\left[ {m^2}/{s^2} \\right]$'
wallShearStressLUTColorBar.ComponentTitle = ''
wallShearStressLUTColorBar.HorizontalTitle = 1
wallShearStressLUTColorBar.TitleFontSize = 20
wallShearStressLUTColorBar.LabelFontSize = 20
wallShearStressLUTColorBar.ScalarBarThickness = 24
wallShearStressLUTColorBar.ScalarBarLength = 0.35
wallShearStressLUTColorBar.DrawBackground = 1
wallShearStressLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
wallShearStressLUTColorBar.DrawScalarBarOutline = 1
wallShearStressLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
wallShearStressLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
wallShearStressLUTColorBar.Visibility = 0

# get 2D transfer function for 'Lambda2Field'
lambda2FieldTF2D = GetTransferFunction2D('Lambda2Field')
lambda2FieldTF2D.ScalarRangeInitialized = 1
lambda2FieldTF2D.Range = [-1.0, 1.0, 0.0, 1.0]

# get color transfer function/color map for 'Lambda2Field'
lambda2FieldLUT = GetColorTransferFunction('Lambda2Field')
lambda2FieldLUT.AutomaticRescaleRangeMode = 'Never'
lambda2FieldLUT.TransferFunction2D = lambda2FieldTF2D
lambda2FieldLUT.RGBPoints = [-1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]
lambda2FieldLUT.ColorSpace = 'HSV'
lambda2FieldLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
lambda2FieldLUT.NumberOfTableValues = 21
lambda2FieldLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for lambda2FieldLUT in view renderView1
lambda2FieldLUTColorBar = GetScalarBar(lambda2FieldLUT, renderView1)
lambda2FieldLUTColorBar.AutoOrient = 0
lambda2FieldLUTColorBar.Orientation = 'Horizontal'
lambda2FieldLUTColorBar.WindowLocation = 'Upper Center'
lambda2FieldLUTColorBar.Title = '$\\lambda_2 {, } \\;  \\left[ {m^2}/{s^2} \\right]$'
lambda2FieldLUTColorBar.ComponentTitle = ''
lambda2FieldLUTColorBar.HorizontalTitle = 1
lambda2FieldLUTColorBar.TitleFontSize = 20
lambda2FieldLUTColorBar.LabelFontSize = 20
lambda2FieldLUTColorBar.ScalarBarThickness = 24
lambda2FieldLUTColorBar.ScalarBarLength = 0.35
lambda2FieldLUTColorBar.DrawBackground = 1
lambda2FieldLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
lambda2FieldLUTColorBar.DrawScalarBarOutline = 1
lambda2FieldLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
lambda2FieldLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
lambda2FieldLUTColorBar.Visibility = 0

# get 2D transfer function for 'Q'
qTF2D = GetTransferFunction2D('Q')

# get color transfer function/color map for 'Q'
qLUT = GetColorTransferFunction('Q')
qLUT.AutomaticRescaleRangeMode = 'Never'
qLUT.TransferFunction2D = qTF2D
qLUT.RGBPoints = [-6.322246551513672, 0.0, 0.0, 1.0, 24.889358520507812, 1.0, 0.0, 0.0]
qLUT.ColorSpace = 'HSV'
qLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
qLUT.NumberOfTableValues = 21
qLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for qLUT in view renderView1
qLUTColorBar = GetScalarBar(qLUT, renderView1)
qLUTColorBar.AutoOrient = 0
qLUTColorBar.Orientation = 'Horizontal'
qLUTColorBar.WindowLocation = 'Upper Center'
qLUTColorBar.Title = '$Q {, } \\;  \\left[ s^{-2} \\right]$'
qLUTColorBar.ComponentTitle = ''
qLUTColorBar.HorizontalTitle = 1
qLUTColorBar.TitleFontSize = 20
qLUTColorBar.LabelFontSize = 20
qLUTColorBar.ScalarBarThickness = 24
qLUTColorBar.ScalarBarLength = 0.35
qLUTColorBar.DrawBackground = 1
qLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
qLUTColorBar.DrawScalarBarOutline = 1
qLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
qLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
qLUTColorBar.Visibility = 0

# get 2D transfer function for 'staticCoeffP'
staticCoeffPTF2D = GetTransferFunction2D('staticCoeffP')

# get color transfer function/color map for 'staticCoeffP'
staticCoeffPLUT = GetColorTransferFunction('staticCoeffP')
staticCoeffPLUT.AutomaticRescaleRangeMode = 'Never'
staticCoeffPLUT.TransferFunction2D = staticCoeffPTF2D
staticCoeffPLUT.RGBPoints = [-1.6469745635986328, 0.0, 0.0, 1.0, 1.0444533824920654, 1.0, 0.0, 0.0]
staticCoeffPLUT.ColorSpace = 'HSV'
staticCoeffPLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
staticCoeffPLUT.NumberOfTableValues = 21
staticCoeffPLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for staticCoeffPLUT in view renderView1
staticCoeffPLUTColorBar = GetScalarBar(staticCoeffPLUT, renderView1)
staticCoeffPLUTColorBar.AutoOrient = 0
staticCoeffPLUTColorBar.Orientation = 'Horizontal'
staticCoeffPLUTColorBar.WindowLocation = 'Upper Center'
staticCoeffPLUTColorBar.Title = '$C_p$'
staticCoeffPLUTColorBar.ComponentTitle = ''
staticCoeffPLUTColorBar.HorizontalTitle = 1
staticCoeffPLUTColorBar.TitleFontSize = 20
staticCoeffPLUTColorBar.LabelFontSize = 20
staticCoeffPLUTColorBar.ScalarBarThickness = 24
staticCoeffPLUTColorBar.ScalarBarLength = 0.35
staticCoeffPLUTColorBar.DrawBackground = 1
staticCoeffPLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
staticCoeffPLUTColorBar.DrawScalarBarOutline = 1
staticCoeffPLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
staticCoeffPLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
staticCoeffPLUTColorBar.Visibility = 0

# get 2D transfer function for 'staticP'
staticPTF2D = GetTransferFunction2D('staticP')

# get color transfer function/color map for 'staticP'
staticPLUT = GetColorTransferFunction('staticP')
staticPLUT.AutomaticRescaleRangeMode = 'Never'
staticPLUT.TransferFunction2D = staticPTF2D
staticPLUT.RGBPoints = [-82348.71875, 0.0, 0.0, 1.0, 52222.66796875, 1.0, 0.0, 0.0]
staticPLUT.ColorSpace = 'HSV'
staticPLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
staticPLUT.NumberOfTableValues = 21
staticPLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for staticPLUT in view renderView1
staticPLUTColorBar = GetScalarBar(staticPLUT, renderView1)
staticPLUTColorBar.AutoOrient = 0
staticPLUTColorBar.Orientation = 'Horizontal'
staticPLUTColorBar.WindowLocation = 'Upper Center'
staticPLUTColorBar.Title = '$p_s {, } \\;  \\left[ Pa \\right]$'
staticPLUTColorBar.ComponentTitle = ''
staticPLUTColorBar.TitleFontSize = 20
staticPLUTColorBar.LabelFontSize = 20
staticPLUTColorBar.ScalarBarThickness = 20
staticPLUTColorBar.ScalarBarLength = 0.35
staticPLUTColorBar.DrawBackground = 1
staticPLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
staticPLUTColorBar.DrawScalarBarOutline = 1
staticPLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
staticPLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
staticPLUTColorBar.Visibility = 0

# get 2D transfer function for 'totalCoeffP'
totalCoeffPTF2D = GetTransferFunction2D('totalCoeffP')

# get color transfer function/color map for 'totalCoeffP'
totalCoeffPLUT = GetColorTransferFunction('totalCoeffP')
totalCoeffPLUT.AutomaticRescaleRangeMode = 'Never'
totalCoeffPLUT.TransferFunction2D = totalCoeffPTF2D
totalCoeffPLUT.RGBPoints = [-658.789794921875, 0.0, 0.0, 1.0, 591.94775390625, 1.0, 0.0, 0.0]
totalCoeffPLUT.ColorSpace = 'HSV'
totalCoeffPLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
totalCoeffPLUT.NumberOfTableValues = 21
totalCoeffPLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for totalCoeffPLUT in view renderView1
totalCoeffPLUTColorBar = GetScalarBar(totalCoeffPLUT, renderView1)
totalCoeffPLUTColorBar.AutoOrient = 0
totalCoeffPLUTColorBar.Orientation = 'Horizontal'
totalCoeffPLUTColorBar.WindowLocation = 'Upper Center'
totalCoeffPLUTColorBar.Title = '${\\left(C_p\\right)}_t$'
totalCoeffPLUTColorBar.ComponentTitle = ''
totalCoeffPLUTColorBar.HorizontalTitle = 1
totalCoeffPLUTColorBar.TitleFontSize = 20
totalCoeffPLUTColorBar.LabelFontSize = 20
totalCoeffPLUTColorBar.ScalarBarThickness = 24
totalCoeffPLUTColorBar.ScalarBarLength = 0.35
totalCoeffPLUTColorBar.DrawBackground = 1
totalCoeffPLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
totalCoeffPLUTColorBar.DrawScalarBarOutline = 1
totalCoeffPLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
totalCoeffPLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
totalCoeffPLUTColorBar.Visibility = 0

# get 2D transfer function for 'totalP'
totalPTF2D = GetTransferFunction2D('totalP')

# get color transfer function/color map for 'totalP'
totalPLUT = GetColorTransferFunction('totalP')
totalPLUT.AutomaticRescaleRangeMode = 'Never'
totalPLUT.TransferFunction2D = totalPTF2D
totalPLUT.RGBPoints = [-82348.71875, 0.0, 0.0, 1.0, 73993.46875, 1.0, 0.0, 0.0]
totalPLUT.ColorSpace = 'HSV'
totalPLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
totalPLUT.NumberOfTableValues = 21
totalPLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for totalPLUT in view renderView1
totalPLUTColorBar = GetScalarBar(totalPLUT, renderView1)
totalPLUTColorBar.AutoOrient = 0
totalPLUTColorBar.Orientation = 'Horizontal'
totalPLUTColorBar.WindowLocation = 'Upper Center'
totalPLUTColorBar.Position = [0.32778581765557163, 0.8906532968617349]
totalPLUTColorBar.Title = '$p_t {, } \\;  \\left[ Pa \\right]$'
totalPLUTColorBar.ComponentTitle = ''
totalPLUTColorBar.HorizontalTitle = 1
totalPLUTColorBar.TitleFontSize = 20
totalPLUTColorBar.LabelFontSize = 20
totalPLUTColorBar.ScalarBarThickness = 24
totalPLUTColorBar.ScalarBarLength = 0.35
totalPLUTColorBar.DrawBackground = 1
totalPLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
totalPLUTColorBar.DrawScalarBarOutline = 1
totalPLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
totalPLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
totalPLUTColorBar.Visibility = 0

# get color legend/bar for yPlusLUT in view renderView1
yPlusLUTColorBar = GetScalarBar(yPlusLUT, renderView1)
yPlusLUTColorBar.AutoOrient = 0
yPlusLUTColorBar.Orientation = 'Horizontal'
yPlusLUTColorBar.WindowLocation = 'Upper Center'
yPlusLUTColorBar.Title = '$y^+ $'
yPlusLUTColorBar.ComponentTitle = ''
yPlusLUTColorBar.HorizontalTitle = 1
yPlusLUTColorBar.TitleFontSize = 20
yPlusLUTColorBar.LabelFontSize = 20
yPlusLUTColorBar.ScalarBarThickness = 24
yPlusLUTColorBar.ScalarBarLength = 0.35
yPlusLUTColorBar.DrawBackground = 1
yPlusLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
yPlusLUTColorBar.DrawScalarBarOutline = 1
yPlusLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
yPlusLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
yPlusLUTColorBar.Visibility = 0

# get 2D transfer function for 'HelicityDensity'
helicityDensityTF2D = GetTransferFunction2D('HelicityDensity')

# get color transfer function/color map for 'HelicityDensity'
helicityDensityLUT = GetColorTransferFunction('HelicityDensity')
helicityDensityLUT.AutomaticRescaleRangeMode = 'Never'
helicityDensityLUT.TransferFunction2D = helicityDensityTF2D
helicityDensityLUT.RGBPoints = [-7.016012547985588e-16, 0.0, 0.0, 1.0, 7.432680230838595e-16, 1.0, 0.0, 0.0]
helicityDensityLUT.ColorSpace = 'HSV'
helicityDensityLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
helicityDensityLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for helicityDensityLUT in view renderView1
helicityDensityLUTColorBar = GetScalarBar(helicityDensityLUT, renderView1)
helicityDensityLUTColorBar.Title = 'HelicityDensity'
helicityDensityLUTColorBar.ComponentTitle = ''

# set color bar visibility
helicityDensityLUTColorBar.Visibility = 0

# get 2D transfer function for 'NormalizedHelicity'
normalizedHelicityTF2D = GetTransferFunction2D('NormalizedHelicity')

# get color transfer function/color map for 'NormalizedHelicity'
normalizedHelicityLUT = GetColorTransferFunction('NormalizedHelicity')
normalizedHelicityLUT.AutomaticRescaleRangeMode = 'Never'
normalizedHelicityLUT.TransferFunction2D = normalizedHelicityTF2D
normalizedHelicityLUT.RGBPoints = [-0.8633255362510681, 0.0, 0.0, 1.0, 0.49033090472221375, 1.0, 0.0, 0.0]
normalizedHelicityLUT.ColorSpace = 'HSV'
normalizedHelicityLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
normalizedHelicityLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for normalizedHelicityLUT in view renderView1
normalizedHelicityLUTColorBar = GetScalarBar(normalizedHelicityLUT, renderView1)
normalizedHelicityLUTColorBar.AutoOrient = 0
normalizedHelicityLUTColorBar.Orientation = 'Horizontal'
normalizedHelicityLUTColorBar.WindowLocation = 'Upper Center'
normalizedHelicityLUTColorBar.Title = 'NormalizedHelicity'
normalizedHelicityLUTColorBar.ComponentTitle = ''
normalizedHelicityLUTColorBar.HorizontalTitle = 1
normalizedHelicityLUTColorBar.TitleFontSize = 20
normalizedHelicityLUTColorBar.LabelFontSize = 20
normalizedHelicityLUTColorBar.ScalarBarThickness = 24
normalizedHelicityLUTColorBar.ScalarBarLength = 0.35
normalizedHelicityLUTColorBar.DrawBackground = 1
normalizedHelicityLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
normalizedHelicityLUTColorBar.DrawScalarBarOutline = 1
normalizedHelicityLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
normalizedHelicityLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
normalizedHelicityLUTColorBar.Visibility = 0

# get 2D transfer function for 'V0'
v0TF2D = GetTransferFunction2D('V0')

# get color transfer function/color map for 'V0'
v0LUT = GetColorTransferFunction('V0')
v0LUT.TransferFunction2D = v0TF2D
v0LUT.RGBPoints = [0.00015018903650343418, 0.231373, 0.298039, 0.752941, 1.3302999661536887, 0.865003, 0.865003, 0.865003, 2.660449743270874, 0.705882, 0.0156863, 0.14902]
v0LUT.ScalarRangeInitialized = 1.0

# get color legend/bar for v0LUT in view renderView1
v0LUTColorBar = GetScalarBar(v0LUT, renderView1)
v0LUTColorBar.AutoOrient = 0
v0LUTColorBar.Orientation = 'Horizontal'
v0LUTColorBar.WindowLocation = 'Upper Center'
v0LUTColorBar.Title = 'V0'
v0LUTColorBar.ComponentTitle = ''
v0LUTColorBar.HorizontalTitle = 1
v0LUTColorBar.TitleFontSize = 20
v0LUTColorBar.LabelFontSize = 20
v0LUTColorBar.ScalarBarThickness = 24
v0LUTColorBar.ScalarBarLength = 0.35
v0LUTColorBar.DrawBackground = 1
v0LUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
v0LUTColorBar.DrawScalarBarOutline = 1
v0LUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
v0LUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
v0LUTColorBar.Visibility = 0

# get 2D transfer function for 'AbsHelicity'
absHelicityTF2D = GetTransferFunction2D('AbsHelicity')

# get color transfer function/color map for 'AbsHelicity'
absHelicityLUT = GetColorTransferFunction('AbsHelicity')
absHelicityLUT.AutomaticRescaleRangeMode = 'Never'
absHelicityLUT.TransferFunction2D = absHelicityTF2D
absHelicityLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 6.469069208975231e-18, 0.865003, 0.865003, 0.865003, 1.2938138417950463e-17, 0.705882, 0.0156863, 0.14902]
absHelicityLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for absHelicityLUT in view renderView1
absHelicityLUTColorBar = GetScalarBar(absHelicityLUT, renderView1)
absHelicityLUTColorBar.AutoOrient = 0
absHelicityLUTColorBar.Orientation = 'Horizontal'
absHelicityLUTColorBar.WindowLocation = 'Upper Center'
absHelicityLUTColorBar.Title = '$H {, } \\;  \\left[ {m^4}/{s^2} \\right]$'
absHelicityLUTColorBar.ComponentTitle = ''
absHelicityLUTColorBar.HorizontalTitle = 1
absHelicityLUTColorBar.TitleFontSize = 20
absHelicityLUTColorBar.LabelFontSize = 20
absHelicityLUTColorBar.ScalarBarThickness = 24
absHelicityLUTColorBar.ScalarBarLength = 0.35
absHelicityLUTColorBar.DrawBackground = 1
absHelicityLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
absHelicityLUTColorBar.DrawScalarBarOutline = 1
absHelicityLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]

# set color bar visibility
absHelicityLUTColorBar.Visibility = 0

# get 2D transfer function for 'DQ'
dQTF2D = GetTransferFunction2D('DQ')

# get color transfer function/color map for 'DQ'
dQLUT = GetColorTransferFunction('DQ')
dQLUT.AutomaticRescaleRangeMode = 'Never'
dQLUT.TransferFunction2D = dQTF2D
dQLUT.RGBPoints = [0.001490546218613805, 0.0, 0.0, 1.0, 12699.925072231159, 1.0, 0.0, 0.0]
dQLUT.ColorSpace = 'HSV'
dQLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
dQLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for dQLUT in view renderView1
dQLUTColorBar = GetScalarBar(dQLUT, renderView1)
dQLUTColorBar.AutoOrient = 0
dQLUTColorBar.Orientation = 'Horizontal'
dQLUTColorBar.WindowLocation = 'Upper Center'
dQLUTColorBar.Title = 'DQ'
dQLUTColorBar.ComponentTitle = ''
dQLUTColorBar.HorizontalTitle = 1
dQLUTColorBar.TitleFontSize = 20
dQLUTColorBar.LabelFontSize = 20
dQLUTColorBar.ScalarBarThickness = 24
dQLUTColorBar.ScalarBarLength = 0.35
dQLUTColorBar.DrawBackground = 1
dQLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
dQLUTColorBar.DrawScalarBarOutline = 1
dQLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
dQLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
dQLUTColorBar.Visibility = 0

# get 2D transfer function for 'vorticityMag'
vorticityMagTF2D = GetTransferFunction2D('vorticityMag')
vorticityMagTF2D.ScalarRangeInitialized = 1

# get color transfer function/color map for 'vorticityMag'
vorticityMagLUT = GetColorTransferFunction('vorticityMag')
vorticityMagLUT.AutomaticRescaleRangeMode = 'Never'
vorticityMagLUT.TransferFunction2D = vorticityMagTF2D
vorticityMagLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]
vorticityMagLUT.ColorSpace = 'HSV'
vorticityMagLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
vorticityMagLUT.NumberOfTableValues = 21
vorticityMagLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for vorticityMagLUT in view renderView1
vorticityMagLUTColorBar = GetScalarBar(vorticityMagLUT, renderView1)
vorticityMagLUTColorBar.AutoOrient = 0
vorticityMagLUTColorBar.Orientation = 'Horizontal'
vorticityMagLUTColorBar.WindowLocation = 'Upper Center'
vorticityMagLUTColorBar.Title = '$\\omega  {, } \\;  \\left[ {1}/{s} \\right]$'
vorticityMagLUTColorBar.ComponentTitle = ''
vorticityMagLUTColorBar.HorizontalTitle = 1
vorticityMagLUTColorBar.TitleFontSize = 20
vorticityMagLUTColorBar.LabelFontSize = 20
vorticityMagLUTColorBar.ScalarBarThickness = 24
vorticityMagLUTColorBar.ScalarBarLength = 0.35
vorticityMagLUTColorBar.DrawBackground = 1
vorticityMagLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
vorticityMagLUTColorBar.DrawScalarBarOutline = 1
vorticityMagLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
vorticityMagLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
vorticityMagLUTColorBar.Visibility = 0

# get 2D transfer function for 'VelocityMag'
velocityMagTF2D = GetTransferFunction2D('VelocityMag')

# get color transfer function/color map for 'VelocityMag'
velocityMagLUT = GetColorTransferFunction('VelocityMag')
velocityMagLUT.TransferFunction2D = velocityMagTF2D
velocityMagLUT.RGBPoints = [0.0, 0.0, 0.0, 1.0, 1.3761419854660015, 1.0, 0.0, 0.0]
velocityMagLUT.ColorSpace = 'HSV'
velocityMagLUT.NanColor = [0.498039215686, 0.498039215686, 0.498039215686]
velocityMagLUT.NumberOfTableValues = 21
velocityMagLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for velocityMagLUT in view renderView1
velocityMagLUTColorBar = GetScalarBar(velocityMagLUT, renderView1)
velocityMagLUTColorBar.AutoOrient = 0
velocityMagLUTColorBar.Orientation = 'Horizontal'
velocityMagLUTColorBar.WindowLocation = 'Upper Center'
velocityMagLUTColorBar.Title = '$U {, } \\;  \\left[ {m}/{s} \\right]$'
velocityMagLUTColorBar.ComponentTitle = ''
velocityMagLUTColorBar.TitleFontSize = 20
velocityMagLUTColorBar.LabelFontSize = 20
velocityMagLUTColorBar.ScalarBarThickness = 24
velocityMagLUTColorBar.ScalarBarLength = 0.35
velocityMagLUTColorBar.DrawBackground = 1
velocityMagLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
velocityMagLUTColorBar.DrawScalarBarOutline = 1
velocityMagLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
velocityMagLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
velocityMagLUTColorBar.Visibility = 0

# get 2D transfer function for 'TrailId'
trailIdTF2D = GetTransferFunction2D('TrailId')

# get color transfer function/color map for 'TrailId'
trailIdLUT = GetColorTransferFunction('TrailId')
trailIdLUT.TransferFunction2D = trailIdTF2D
trailIdLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 10545.0, 0.865003, 0.865003, 0.865003, 21090.0, 0.705882, 0.0156863, 0.14902]
trailIdLUT.NumberOfTableValues = 21
trailIdLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for trailIdLUT in view renderView1
trailIdLUTColorBar = GetScalarBar(trailIdLUT, renderView1)
trailIdLUTColorBar.AutoOrient = 0
trailIdLUTColorBar.Title = 'TrailId'
trailIdLUTColorBar.ComponentTitle = ''
trailIdLUTColorBar.HorizontalTitle = 1
trailIdLUTColorBar.TitleFontSize = 20
trailIdLUTColorBar.LabelFontSize = 20
trailIdLUTColorBar.ScalarBarThickness = 24
trailIdLUTColorBar.ScalarBarLength = 0.35
trailIdLUTColorBar.DrawBackground = 1
trailIdLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
trailIdLUTColorBar.DrawScalarBarOutline = 1
trailIdLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
trailIdLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
trailIdLUTColorBar.Visibility = 0

# get 2D transfer function for 'p'
pTF2D_1 = GetTransferFunction2D('p')

# get color transfer function/color map for 'p'
pLUT_1 = GetColorTransferFunction('p')
pLUT_1.TransferFunction2D = pTF2D_1
pLUT_1.RGBPoints = [-0.7230019569396973, 0.231373, 0.298039, 0.752941, -0.10164180397987366, 0.865003, 0.865003, 0.865003, 0.51971834897995, 0.705882, 0.0156863, 0.14902]
pLUT_1.ScalarRangeInitialized = 1.0

# get color legend/bar for pLUT_1 in view renderView1
pLUT_1ColorBar = GetScalarBar(pLUT_1, renderView1)
pLUT_1ColorBar.WindowLocation = 'Upper Right Corner'
pLUT_1ColorBar.Title = 'p'
pLUT_1ColorBar.ComponentTitle = ''

# set color bar visibility
pLUT_1ColorBar.Visibility = 0

# get color legend/bar for velocityLUT in view renderView1
velocityLUTColorBar = GetScalarBar(velocityLUT, renderView1)
velocityLUTColorBar.AutoOrient = 0
velocityLUTColorBar.Orientation = 'Horizontal'
velocityLUTColorBar.WindowLocation = 'Upper Center'
velocityLUTColorBar.Title = '$U {, } \\;  \\left[ {m}/{s} \\right]$'
velocityLUTColorBar.ComponentTitle = ''
velocityLUTColorBar.HorizontalTitle = 1
velocityLUTColorBar.TitleFontSize = 20
velocityLUTColorBar.LabelFontSize = 20
velocityLUTColorBar.ScalarBarThickness = 24
velocityLUTColorBar.ScalarBarLength = 0.35
velocityLUTColorBar.DrawBackground = 1
velocityLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
velocityLUTColorBar.DrawScalarBarOutline = 1
velocityLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
velocityLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
velocityLUTColorBar.Visibility = 0

# get 2D transfer function for 'ParticleId'
particleIdTF2D = GetTransferFunction2D('ParticleId')

# get color transfer function/color map for 'ParticleId'
particleIdLUT = GetColorTransferFunction('ParticleId')
particleIdLUT.TransferFunction2D = particleIdTF2D
particleIdLUT.RGBPoints = [2434451.0, 0.231373, 0.298039, 0.752941, 2447752.5, 0.865003, 0.865003, 0.865003, 2461054.0, 0.705882, 0.0156863, 0.14902]
particleIdLUT.NumberOfTableValues = 21
particleIdLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for particleIdLUT in view renderView1
particleIdLUTColorBar = GetScalarBar(particleIdLUT, renderView1)
particleIdLUTColorBar.AutoOrient = 0
particleIdLUTColorBar.WindowLocation = 'Upper Left Corner'
particleIdLUTColorBar.Title = 'ParticleId'
particleIdLUTColorBar.ComponentTitle = ''
particleIdLUTColorBar.HorizontalTitle = 1
particleIdLUTColorBar.TitleFontSize = 20
particleIdLUTColorBar.LabelFontSize = 20
particleIdLUTColorBar.ScalarBarThickness = 24
particleIdLUTColorBar.ScalarBarLength = 0.35
particleIdLUTColorBar.DrawBackground = 1
particleIdLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
particleIdLUTColorBar.DrawScalarBarOutline = 1
particleIdLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]

# set color bar visibility
particleIdLUTColorBar.Visibility = 0

# get 2D transfer function for 'ParticleAge'
particleAgeTF2D = GetTransferFunction2D('ParticleAge')

# get color transfer function/color map for 'ParticleAge'
particleAgeLUT = GetColorTransferFunction('ParticleAge')
particleAgeLUT.TransferFunction2D = particleAgeTF2D
particleAgeLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 0.012500000186264515, 0.865003, 0.865003, 0.865003, 0.02500000037252903, 0.705882, 0.0156863, 0.14902]
particleAgeLUT.NumberOfTableValues = 21
particleAgeLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for particleAgeLUT in view renderView1
particleAgeLUTColorBar = GetScalarBar(particleAgeLUT, renderView1)
particleAgeLUTColorBar.AutoOrient = 0
particleAgeLUTColorBar.WindowLocation = 'Upper Left Corner'
particleAgeLUTColorBar.Title = 'ParticleAge'
particleAgeLUTColorBar.ComponentTitle = ''
particleAgeLUTColorBar.HorizontalTitle = 1
particleAgeLUTColorBar.TitleFontSize = 20
particleAgeLUTColorBar.LabelFontSize = 20
particleAgeLUTColorBar.ScalarBarThickness = 24
particleAgeLUTColorBar.ScalarBarLength = 0.35
particleAgeLUTColorBar.DrawBackground = 1
particleAgeLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
particleAgeLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
particleAgeLUTColorBar.Visibility = 0

# get 2D transfer function for 'InjectedPointId'
injectedPointIdTF2D = GetTransferFunction2D('InjectedPointId')

# get color transfer function/color map for 'InjectedPointId'
injectedPointIdLUT = GetColorTransferFunction('InjectedPointId')
injectedPointIdLUT.TransferFunction2D = injectedPointIdTF2D
injectedPointIdLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 6689.5, 0.865003, 0.865003, 0.865003, 13379.0, 0.705882, 0.0156863, 0.14902]
injectedPointIdLUT.NumberOfTableValues = 21
injectedPointIdLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for injectedPointIdLUT in view renderView1
injectedPointIdLUTColorBar = GetScalarBar(injectedPointIdLUT, renderView1)
injectedPointIdLUTColorBar.AutoOrient = 0
injectedPointIdLUTColorBar.WindowLocation = 'Upper Left Corner'
injectedPointIdLUTColorBar.Title = 'InjectedPointId'
injectedPointIdLUTColorBar.ComponentTitle = ''
injectedPointIdLUTColorBar.HorizontalTitle = 1
injectedPointIdLUTColorBar.TitleFontSize = 20
injectedPointIdLUTColorBar.LabelFontSize = 20
injectedPointIdLUTColorBar.ScalarBarThickness = 24
injectedPointIdLUTColorBar.ScalarBarLength = 0.35
injectedPointIdLUTColorBar.DrawBackground = 1
injectedPointIdLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
injectedPointIdLUTColorBar.DrawScalarBarOutline = 1
injectedPointIdLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
injectedPointIdLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
injectedPointIdLUTColorBar.Visibility = 0

# get 2D transfer function for 'InjectionStepId'
injectionStepIdTF2D = GetTransferFunction2D('InjectionStepId')

# get color transfer function/color map for 'InjectionStepId'
injectionStepIdLUT = GetColorTransferFunction('InjectionStepId')
injectionStepIdLUT.TransferFunction2D = injectionStepIdTF2D
injectionStepIdLUT.RGBPoints = [183.0, 0.231373, 0.298039, 0.752941, 183.5, 0.865003, 0.865003, 0.865003, 184.0, 0.705882, 0.0156863, 0.14902]
injectionStepIdLUT.NumberOfTableValues = 21
injectionStepIdLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for injectionStepIdLUT in view renderView1
injectionStepIdLUTColorBar = GetScalarBar(injectionStepIdLUT, renderView1)
injectionStepIdLUTColorBar.AutoOrient = 0
injectionStepIdLUTColorBar.WindowLocation = 'Upper Left Corner'
injectionStepIdLUTColorBar.Title = 'InjectionStepId'
injectionStepIdLUTColorBar.ComponentTitle = ''
injectionStepIdLUTColorBar.HorizontalTitle = 1
injectionStepIdLUTColorBar.TitleFontSize = 20
injectionStepIdLUTColorBar.LabelFontSize = 20
injectionStepIdLUTColorBar.ScalarBarThickness = 24
injectionStepIdLUTColorBar.ScalarBarLength = 0.35
injectionStepIdLUTColorBar.DrawBackground = 1
injectionStepIdLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
injectionStepIdLUTColorBar.DrawScalarBarOutline = 1
injectionStepIdLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
injectionStepIdLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
injectionStepIdLUTColorBar.Visibility = 0

# get 2D transfer function for 'ParticleSourceId'
particleSourceIdTF2D = GetTransferFunction2D('ParticleSourceId')

# get color transfer function/color map for 'ParticleSourceId'
particleSourceIdLUT = GetColorTransferFunction('ParticleSourceId')
particleSourceIdLUT.TransferFunction2D = particleSourceIdTF2D
particleSourceIdLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 5.878906683738906e-39, 0.865003, 0.865003, 0.865003, 1.1757813367477812e-38, 0.705882, 0.0156863, 0.14902]
particleSourceIdLUT.NumberOfTableValues = 21
particleSourceIdLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for particleSourceIdLUT in view renderView1
particleSourceIdLUTColorBar = GetScalarBar(particleSourceIdLUT, renderView1)
particleSourceIdLUTColorBar.AutoOrient = 0
particleSourceIdLUTColorBar.WindowLocation = 'Upper Left Corner'
particleSourceIdLUTColorBar.Title = 'ParticleSourceId'
particleSourceIdLUTColorBar.ComponentTitle = ''
particleSourceIdLUTColorBar.HorizontalTitle = 1
particleSourceIdLUTColorBar.TitleFontSize = 20
particleSourceIdLUTColorBar.LabelFontSize = 20
particleSourceIdLUTColorBar.ScalarBarThickness = 24
particleSourceIdLUTColorBar.ScalarBarLength = 0.35
particleSourceIdLUTColorBar.DrawBackground = 1
particleSourceIdLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
particleSourceIdLUTColorBar.DrawScalarBarOutline = 1
particleSourceIdLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
particleSourceIdLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
particleSourceIdLUTColorBar.Visibility = 0

# get 2D transfer function for 'AngularVelocity'
angularVelocityTF2D = GetTransferFunction2D('AngularVelocity')

# get color transfer function/color map for 'AngularVelocity'
angularVelocityLUT = GetColorTransferFunction('AngularVelocity')
angularVelocityLUT.TransferFunction2D = angularVelocityTF2D
angularVelocityLUT.RGBPoints = [-2.024523432198836e-14, 0.231373, 0.298039, 0.752941, 4.051443290012044e-16, 0.865003, 0.865003, 0.865003, 2.105552297999077e-14, 0.705882, 0.0156863, 0.14902]
angularVelocityLUT.NumberOfTableValues = 21
angularVelocityLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for angularVelocityLUT in view renderView1
angularVelocityLUTColorBar = GetScalarBar(angularVelocityLUT, renderView1)
angularVelocityLUTColorBar.AutoOrient = 0
angularVelocityLUTColorBar.WindowLocation = 'Upper Left Corner'
angularVelocityLUTColorBar.Title = 'AngularVelocity'
angularVelocityLUTColorBar.ComponentTitle = ''
angularVelocityLUTColorBar.HorizontalTitle = 1
angularVelocityLUTColorBar.TitleFontSize = 20
angularVelocityLUTColorBar.LabelFontSize = 20
angularVelocityLUTColorBar.ScalarBarThickness = 24
angularVelocityLUTColorBar.ScalarBarLength = 0.35
angularVelocityLUTColorBar.DrawBackground = 1
angularVelocityLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
angularVelocityLUTColorBar.DrawScalarBarOutline = 1
angularVelocityLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
angularVelocityLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
angularVelocityLUTColorBar.Visibility = 0

# get 2D transfer function for 'ErrorCode'
errorCodeTF2D = GetTransferFunction2D('ErrorCode')

# get color transfer function/color map for 'ErrorCode'
errorCodeLUT = GetColorTransferFunction('ErrorCode')
errorCodeLUT.TransferFunction2D = errorCodeTF2D
errorCodeLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 5.878906683738906e-39, 0.865003, 0.865003, 0.865003, 1.1757813367477812e-38, 0.705882, 0.0156863, 0.14902]
errorCodeLUT.NumberOfTableValues = 21
errorCodeLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for errorCodeLUT in view renderView1
errorCodeLUTColorBar = GetScalarBar(errorCodeLUT, renderView1)
errorCodeLUTColorBar.AutoOrient = 0
errorCodeLUTColorBar.WindowLocation = 'Upper Left Corner'
errorCodeLUTColorBar.Title = 'ErrorCode'
errorCodeLUTColorBar.ComponentTitle = ''
errorCodeLUTColorBar.HorizontalTitle = 1
errorCodeLUTColorBar.TitleFontSize = 20
errorCodeLUTColorBar.LabelFontSize = 20
errorCodeLUTColorBar.ScalarBarThickness = 24
errorCodeLUTColorBar.ScalarBarLength = 0.35
errorCodeLUTColorBar.DrawBackground = 1
errorCodeLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
errorCodeLUTColorBar.DrawScalarBarOutline = 1
errorCodeLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
errorCodeLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
errorCodeLUTColorBar.Visibility = 0

# get 2D transfer function for 'Rotation'
rotationTF2D = GetTransferFunction2D('Rotation')

# get color transfer function/color map for 'Rotation'
rotationLUT = GetColorTransferFunction('Rotation')
rotationLUT.TransferFunction2D = rotationTF2D
rotationLUT.RGBPoints = [-3.5914335741460413e-12, 0.231373, 0.298039, 0.752941, 7.230587656392728e-14, 0.865003, 0.865003, 0.865003, 3.736045327273896e-12, 0.705882, 0.0156863, 0.14902]
rotationLUT.NumberOfTableValues = 21
rotationLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for rotationLUT in view renderView1
rotationLUTColorBar = GetScalarBar(rotationLUT, renderView1)
rotationLUTColorBar.AutoOrient = 0
rotationLUTColorBar.WindowLocation = 'Upper Left Corner'
rotationLUTColorBar.Title = 'Rotation'
rotationLUTColorBar.ComponentTitle = ''
rotationLUTColorBar.HorizontalTitle = 1
rotationLUTColorBar.ScalarBarThickness = 24
rotationLUTColorBar.ScalarBarLength = 0.35
rotationLUTColorBar.DrawBackground = 1
rotationLUTColorBar.BackgroundColor = [1.0, 1.0, 1.0, 1.0]
rotationLUTColorBar.DrawScalarBarOutline = 1
rotationLUTColorBar.ScalarBarOutlineColor = [0.0, 0.0, 0.0]
rotationLUTColorBar.RangeLabelFormat = '%-#.3f'

# set color bar visibility
rotationLUTColorBar.Visibility = 0

# hide data in view
Hide(casefoam, renderView1)

# show color legend
temporalInterpolator1Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(temporalInterpolator1, renderView1)

# hide data in view
Hide(slice1, renderView1)

# hide data in view
Hide(calculatorVelocity, renderView1)

# hide data in view
Hide(tableToPoints1, renderView1)

# show color legend
streakLine1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'ParticleSourceId'
particleSourceIdPWF = GetOpacityTransferFunction('ParticleSourceId')
particleSourceIdPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]
particleSourceIdPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'Velocity'
velocityPWF = GetOpacityTransferFunction('Velocity')
velocityPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.4313095515380458, 1.0, 0.5, 0.0]
velocityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'NormalizedHelicity'
normalizedHelicityPWF = GetOpacityTransferFunction('NormalizedHelicity')
normalizedHelicityPWF.Points = [-0.8633255362510681, 0.0, 0.5, 0.0, 0.49033090472221375, 1.0, 0.5, 0.0]
normalizedHelicityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'staticCoeffP'
staticCoeffPPWF = GetOpacityTransferFunction('staticCoeffP')
staticCoeffPPWF.Points = [-1.6469745635986328, 0.0, 0.5, 0.0, 1.0444533824920654, 1.0, 0.5, 0.0]
staticCoeffPPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'ParticleId'
particleIdPWF = GetOpacityTransferFunction('ParticleId')
particleIdPWF.Points = [2434451.0, 0.0, 0.5, 0.0, 2461054.0, 1.0, 0.5, 0.0]
particleIdPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'AngularVelocity'
angularVelocityPWF = GetOpacityTransferFunction('AngularVelocity')
angularVelocityPWF.Points = [-2.024523432198836e-14, 0.0, 0.5, 0.0, 2.105552297999077e-14, 1.0, 0.5, 0.0]
angularVelocityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'VelocityMag'
velocityMagPWF = GetOpacityTransferFunction('VelocityMag')
velocityMagPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.3761419854660015, 1.0, 0.5, 0.0]
velocityMagPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'vorticity'
vorticityPWF = GetOpacityTransferFunction('vorticity')
vorticityPWF.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
vorticityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'V0'
v0PWF = GetOpacityTransferFunction('V0')
v0PWF.Points = [0.00015018903650343418, 0.0, 0.5, 0.0, 2.660449743270874, 1.0, 0.5, 0.0]
v0PWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'staticP'
staticPPWF = GetOpacityTransferFunction('staticP')
staticPPWF.Points = [-82348.71875, 0.0, 0.5, 0.0, 52222.66796875, 1.0, 0.5, 0.0]
staticPPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'ErrorCode'
errorCodePWF = GetOpacityTransferFunction('ErrorCode')
errorCodePWF.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]
errorCodePWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'ParticleAge'
particleAgePWF = GetOpacityTransferFunction('ParticleAge')
particleAgePWF.Points = [0.0, 0.0, 0.5, 0.0, 0.02500000037252903, 1.0, 0.5, 0.0]
particleAgePWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'LambVectorField'
lambVectorFieldPWF = GetOpacityTransferFunction('LambVectorField')
lambVectorFieldPWF.Points = [0.0, 0.0, 0.5, 0.0, 16.98756221355132, 1.0, 0.5, 0.0]
lambVectorFieldPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'AbsHelicity'
absHelicityPWF = GetOpacityTransferFunction('AbsHelicity')
absHelicityPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.2938138417950463e-17, 1.0, 0.5, 0.0]
absHelicityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'totalCoeffP'
totalCoeffPPWF = GetOpacityTransferFunction('totalCoeffP')
totalCoeffPPWF.Points = [-658.789794921875, 0.0, 0.5, 0.0, 591.94775390625, 1.0, 0.5, 0.0]
totalCoeffPPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'TrailId'
trailIdPWF = GetOpacityTransferFunction('TrailId')
trailIdPWF.Points = [0.0, 0.0, 0.5, 0.0, 21090.0, 1.0, 0.5, 0.0]
trailIdPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'Vorticity'
vorticityPWF_1 = GetOpacityTransferFunction('Vorticity')
vorticityPWF_1.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'Rotation'
rotationPWF = GetOpacityTransferFunction('Rotation')
rotationPWF.Points = [-3.5914335741460413e-12, 0.0, 0.5, 0.0, 3.736045327273896e-12, 1.0, 0.5, 0.0]
rotationPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')
pPWF.Points = [-0.8234872817993164, 0.0, 0.5, 0.0, 0.5222266912460327, 1.0, 0.5, 0.0]
pPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'vorticityMag'
vorticityMagPWF = GetOpacityTransferFunction('vorticityMag')
vorticityMagPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'InjectedPointId'
injectedPointIdPWF = GetOpacityTransferFunction('InjectedPointId')
injectedPointIdPWF.Points = [0.0, 0.0, 0.5, 0.0, 13379.0, 1.0, 0.5, 0.0]
injectedPointIdPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'DQ'
dQPWF = GetOpacityTransferFunction('DQ')
dQPWF.Points = [0.001490546218613805, 0.0, 0.5, 0.0, 12699.925072231159, 1.0, 0.5, 0.0]
dQPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'totalP'
totalPPWF = GetOpacityTransferFunction('totalP')
totalPPWF.Points = [-82348.71875, 0.0, 0.5, 0.0, 73993.46875, 1.0, 0.5, 0.0]
totalPPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'p'
pPWF_1 = GetOpacityTransferFunction('p')
pPWF_1.Points = [-0.7230019569396973, 0.0, 0.5, 0.0, 0.51971834897995, 1.0, 0.5, 0.0]
pPWF_1.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'Lambda2Field'
lambda2FieldPWF = GetOpacityTransferFunction('Lambda2Field')
lambda2FieldPWF.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
lambda2FieldPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'InjectionStepId'
injectionStepIdPWF = GetOpacityTransferFunction('InjectionStepId')
injectionStepIdPWF.Points = [183.0, 0.0, 0.5, 0.0, 184.0, 1.0, 0.5, 0.0]
injectionStepIdPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'wallShearStress'
wallShearStressPWF = GetOpacityTransferFunction('wallShearStress')
wallShearStressPWF.Points = [0.0, 0.0, 0.5, 0.0, 0.16981748115213044, 1.0, 0.5, 0.0]
wallShearStressPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'HelicityDensity'
helicityDensityPWF = GetOpacityTransferFunction('HelicityDensity')
helicityDensityPWF.Points = [-7.016012547985588e-16, 0.0, 0.5, 0.0, 7.432680230838595e-16, 1.0, 0.5, 0.0]
helicityDensityPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'Q'
qPWF = GetOpacityTransferFunction('Q')
qPWF.Points = [-6.322246551513672, 0.0, 0.5, 0.0, 24.889358520507812, 1.0, 0.5, 0.0]
qPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'VorticityZ'
vorticityZPWF = GetOpacityTransferFunction('VorticityZ')
vorticityZPWF.Points = [-31.629619598388672, 0.0, 0.5, 0.0, 32.06517028808594, 1.0, 0.5, 0.0]
vorticityZPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# restore active source
SetActiveSource(streakLine1)
# ----------------------------------------------------------------


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='/home/yevhenv/OpenFOAM/moving_domain/paraview')