from vtk import *
import vtk

# Reslice cursor callback
def ResliceCursorCallback(obj, event):
    for i in range(0,3):
        ps = planeWidgetArray[i].GetPolyDataAlgorithm()
        origin = resliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetOrigin()
        ps.SetOrigin(origin)
        point1 = resliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetPoint1()
        ps.SetPoint1(point1)
        point2 = resliceCursorWidgetArray[i].GetResliceCursorRepresentation().GetPlaneSource().GetPoint2()
        ps.SetPoint2(point2)
        planeWidgetArray[i].UpdatePlacement()

# DICOM reader
reader = vtkDICOMImageReader()
reader.SetDirectoryName(r"C:\Users\lalal\Desktop\imageProcessing\demo\manifest-1701814559353\QIN LUNG CT\QIN-LSC-0009\09-13-2000-1-CT Thorax wCont-24434\7.000000-RENAL VEN.  3.0  B30f-45454")
reader.Update()
imageDims = reader.GetOutput().GetDimensions()


# Mapper and actors for volumez
volumeMapper = vtkPolyDataMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())

volumeActor = vtkActor()
volumeActor.SetMapper(volumeMapper)

# Renderers
renWin = vtkRenderWindow()
RendererArray = [None]*4
for i in range(0,4):
    RendererArray[i] = vtkRenderer()
    renWin.AddRenderer(RendererArray[i])
renWin.SetMultiSamples(0)

# Render window interactor
iren = vtkRenderWindowInteractor()
renWin.SetInteractor(iren)

# Picker
picker = vtkCellPicker()
picker.SetTolerance(0.005)

# Properties
ipwProp = vtkProperty()

# 3D plane widgets
planeWidgetArray = [None]*3
for i in range(0,3):
    planeWidgetArray[i] = vtkImagePlaneWidget()
    planeWidgetArray[i].SetInteractor(iren)
    planeWidgetArray[i].SetPicker(picker)
    planeWidgetArray[i].RestrictPlaneToVolumeOn()
    color = [0, 0, 0 ]
    color[i] = 1
    planeWidgetArray[i].GetPlaneProperty().SetColor(color)
    planeWidgetArray[i].SetTexturePlaneProperty(ipwProp)
    planeWidgetArray[i].TextureInterpolateOff()
    planeWidgetArray[i].SetResliceInterpolateToLinear()
    planeWidgetArray[i].SetInputConnection(reader.GetOutputPort())
    planeWidgetArray[i].SetPlaneOrientation(i)
    planeWidgetArray[i].SetSliceIndex(int(imageDims[i] / 2))
    planeWidgetArray[i].DisplayTextOn()
    planeWidgetArray[i].SetDefaultRenderer(RendererArray[3])
    planeWidgetArray[i].SetWindowLevel(1358, -27, 0)
    planeWidgetArray[i].On()
    planeWidgetArray[i].InteractionOff()

planeWidgetArray[1].SetLookupTable(planeWidgetArray[0].GetLookupTable()) 
planeWidgetArray[2].SetLookupTable(planeWidgetArray[0].GetLookupTable())

# ResliceCursor
resliceCursor = vtkResliceCursor()
resliceCursor.SetImage(reader.GetOutput())
center = reader.GetOutput().GetCenter()
resliceCursor.SetCenter(center[1], center[1], center[2])
resliceCursor.SetThickMode(3)
resliceCursor.SetThickness(.5, .5, .5)
resliceCursor.SetHole(1)

mapping = {1: [0, 2], 2: [0, 1], 0: [1, 2]}

resliceCursorRepArray = [None] * 3
resliceCursorWidgetArray = [None] * 3
viewUp = [[0, 0, -1], [0, 0, -1], [0, 1, 0]]

for i in range(3):
    resliceCursorWidgetArray[i] = vtkResliceCursorWidget()
    resliceCursorRepArray[i] = vtkResliceCursorLineRepresentation()
    resliceCursorWidgetArray[i].SetInteractor(iren)
    resliceCursorWidgetArray[i].SetRepresentation(resliceCursorRepArray[i])

    cursorActor = resliceCursorRepArray[i].GetResliceCursorActor()
    cursorAlgorithm = cursorActor.GetCursorAlgorithm()
    cursorAlgorithm.SetResliceCursor(resliceCursor)
    cursorAlgorithm.SetReslicePlaneNormal(i)

    a, b = mapping[i]
    for prop_idx in (a, b):
        thickSlabProperty = cursorActor.GetThickSlabProperty(prop_idx)
        color = [0, 0, 0]
        color[prop_idx] = 1
        thickSlabProperty.SetColor(color)
        thickSlabProperty.SetRepresentationToWireframe()

    minVal = reader.GetOutput().GetScalarRange()[0]
    reslice = resliceCursorRepArray[i].GetReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetBackgroundColor(minVal, minVal, minVal, minVal)
    reslice.AutoCropOutputOn()
    reslice.Update()

    resliceCursorWidgetArray[i].SetDefaultRenderer(RendererArray[i])
    resliceCursorWidgetArray[i].SetEnabled(True)

    camPos = [0, 0, 0]
    camPos[i] = 1
    camera = RendererArray[i].GetActiveCamera()
    camera.SetPosition(camPos[0], camPos[1], camPos[2])
    camera.ParallelProjectionOn()
    camera.SetViewUp(viewUp[i][0], viewUp[i][1], viewUp[i][2])
    RendererArray[i].ResetCamera()

    resliceCursorWidgetArray[i].AddObserver('InteractionEvent', ResliceCursorCallback)
    resliceCursorWidgetArray[i].On()

    range_color = reader.GetOutput().GetScalarRange()
    resliceCursorRepArray[i].SetWindowLevel(range_color[1] - range_color[0], (range_color[0] + range_color[1]) / 2.0, 0)
    planeWidgetArray[i].SetWindowLevel(range_color[1] - range_color[0], (range_color[0] + range_color[1]) / 2.0, 0)
    resliceCursorRepArray[i].SetLookupTable(resliceCursorRepArray[0].GetLookupTable())
    planeWidgetArray[i].GetColorMap().SetLookupTable(resliceCursorRepArray[0].GetLookupTable())

# Wrap 3D Actor in ren[3]
volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())
volumeMapper.SetBlendModeToComposite()

volumeColor = vtk.vtkColorTransferFunction()
volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
volumeColor.AddRGBPoint(500,  1.0, 0.5, 0.3)
volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

volumeScalarOpacity = vtk.vtkPiecewiseFunction()
volumeScalarOpacity.AddPoint(0,    0.00)
volumeScalarOpacity.AddPoint(500,  0.15)
volumeScalarOpacity.AddPoint(1000, 0.15)
volumeScalarOpacity.AddPoint(1150, 0.85)

volumeGradientOpacity = vtk.vtkPiecewiseFunction()
volumeGradientOpacity.AddPoint(0,   0.0)
volumeGradientOpacity.AddPoint(90,  0.5)
volumeGradientOpacity.AddPoint(100, 1.0)

volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(volumeColor)
volumeProperty.SetScalarOpacity(volumeScalarOpacity)
volumeProperty.SetInterpolationTypeToLinear()
volumeProperty.ShadeOn()
volumeProperty.SetAmbient(0.9)
volumeProperty.SetDiffuse(0.9)
volumeProperty.SetSpecular(0.9)

volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty) 
RendererArray[3].AddActor(volume)

# Background
RendererArray[0].SetBackground(0.3, 0.1, 0.1)
RendererArray[1].SetBackground(0.1, 0.3, 0.1)
RendererArray[2].SetBackground(0.1, 0.1, 0.3)
RendererArray[3].AddActor(volumeActor)
RendererArray[3].SetBackground(0.1, 0.1, 0.1)
renWin.SetSize(600, 600)

# Render
RendererArray[0].SetViewport(0, 0, 0.5, 0.5)
RendererArray[1].SetViewport(0.5, 0, 1, 0.5)
RendererArray[2].SetViewport(0, 0.5, 0.5, 1)
RendererArray[3].SetViewport(0.5, 0.5, 1, 1)
renWin.Render()

# Camera in 3D view
RendererArray[3].GetActiveCamera().Elevation(110)
RendererArray[3].GetActiveCamera().SetViewUp(0, 0, -1)
RendererArray[3].GetActiveCamera().Azimuth(45)
RendererArray[3].GetActiveCamera().Dolly(1.15)
RendererArray[3].ResetCameraClippingRange()

iren.Initialize()
iren.Start()