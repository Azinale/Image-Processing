import vtk
from vtkmodules.all import *

class ResliceCursorCallback(vtk.vtkCallbackCommand):
    def __init__(self):
        self.IPW = [None] * 3
        self.RCW = [None] * 3
        self.volumeRenderer = None
        self.volumeIPW = None
        self.volumeResliceCursor = None
    
    def Execute(self, caller, event, callData):
        ipw = vtk.vtkImagePlaneWidget.SafeDownCast(caller)
        if ipw:
            wl = callData
            if ipw == self.IPW[0]:
                self.IPW[1].SetWindowLevel(wl[0], wl[1], 1)
                self.IPW[2].SetWindowLevel(wl[0], wl[1], 1)
            elif ipw == self.IPW[1]:
                self.IPW[0].SetWindowLevel(wl[0], wl[1], 1)
                self.IPW[2].SetWindowLevel(wl[0], wl[1], 1)
            elif ipw == self.IPW[2]:
                self.IPW[0].SetWindowLevel(wl[0], wl[1], 1)
                self.IPW[1].SetWindowLevel(wl[0], wl[1], 1)
        
        rcw = vtk.vtkResliceCursorWidget.SafeDownCast(caller)
        if rcw:
            rep = vtk.vtkResliceCursorLineRepresentation.SafeDownCast(rcw.GetRepresentation())
            rc = rep.GetResliceCursorActor().GetCursorAlgorithm().GetResliceCursor()
            for i in range(3):
                ps = self.IPW[i].GetPolyDataAlgorithm()
                ps.SetNormal(rc.GetPlane(i).GetNormal())
                ps.SetCenter(rc.GetPlane(i).GetOrigin())
                self.IPW[i].UpdatePlacement()
            
        #     if self.volumeRenderer and self.volumeIPW:
        #         normal = rc.GetPlane(2).GetNormal()  # Assuming axial orientation for simplicity
        #         center = rc.GetCenter()
        #         self.volumeIPW.GetPolyDataAlgorithm().SetNormal(normal)
        #         self.volumeIPW.GetPolyDataAlgorithm().SetCenter(center)
        #         self.volumeIPW.UpdatePlacement()

        # if self.volumeRenderer:
        #     self.volumeRenderer.Render()

        self.RCW[0].Render()

    @staticmethod
    def New():
        return ResliceCursorCallback()

def main():
    # Data constructed
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(r"C:\Users\lalal\Desktop\imageProcessing\demo\manifest-1701814559353\QIN LUNG CT\QIN-LSC-0009\09-13-2000-1-CT Thorax wCont-24434\7.000000-RENAL VEN.  3.0  B30f-45454")
    reader.Update()
    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(reader.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)
    
    renWin = vtk.vtkRenderWindow()
    renWin.SetMultiSamples(0)
    
    ren = [None] * 4
    for i in range(4):
        ren[i] = vtk.vtkRenderer()
        renWin.AddRenderer(ren[i])
    
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    picker = vtk.vtkCellPicker()
    picker.SetTolerance(0.0005)
    
    ipwProp = vtk.vtkProperty()
    planeWidget = [None] * 3
    imageDims = [0] * 3
    reader.GetOutput().GetDimensions(imageDims)
    
    for i in range(3):
        planeWidget[i] = vtk.vtkImagePlaneWidget()
        planeWidget[i].SetInteractor(iren)
        planeWidget[i].SetPicker(picker)
        planeWidget[i].RestrictPlaneToVolumeOn()
        color = [0, 0, 0]
        color[i] = 1
        planeWidget[i].GetPlaneProperty().SetColor(color)
        planeWidget[i].GetPlaneProperty().SetLineWidth(1)
        planeWidget[i].SetTexturePlaneProperty(ipwProp)
        planeWidget[i].TextureInterpolateOff()
        planeWidget[i].SetResliceInterpolateToLinear()
        planeWidget[i].SetInputConnection(reader.GetOutputPort()) 
        planeWidget[i].SetPlaneOrientation(i)
        planeWidget[i].SetSliceIndex(imageDims[i] // 2)
        planeWidget[i].DisplayTextOn()
        planeWidget[i].SetWindowLevel(1358, -27)
        planeWidget[i].SetDefaultRenderer(ren[3])
        planeWidget[i].On()
        planeWidget[i].InteractionOn()

    planeWidget[1].SetLookupTable(planeWidget[0].GetLookupTable())
    planeWidget[2].SetLookupTable(planeWidget[0].GetLookupTable())
    
    cbk = ResliceCursorCallback()
    
    resliceCursor = vtk.vtkResliceCursor() 
    resliceCursor.SetCenter(reader.GetOutput().GetCenter())
    resliceCursor.SetThickMode(0)
    resliceCursor.SetThickness(10, 20, -10)
    resliceCursor.SetImage(reader.GetOutput())
    
    resliceCursorWidget = [None] * 3
    resliceCursorRep = [None] * 3
    viewUp = [(0, 0, -1), (0, 0, 1), (0, 1, 0)]
    
    for i in range(3):
        resliceCursorWidget[i] = vtk.vtkResliceCursorWidget()
        resliceCursorWidget[i].SetInteractor(iren)
        resliceCursorRep[i] = vtk.vtkResliceCursorLineRepresentation()

        resliceCursorRep[i].GetResliceCursorActor().GetCursorAlgorithm().SetReslicePlaneNormal(i)
        resliceCursorRep[i].GetResliceCursorActor().GetCursorAlgorithm().SetResliceCursor(resliceCursor)
        resliceCursorWidget[i].SetRepresentation(resliceCursorRep[i])


        # bonus
        # minVal = reader.GetOutput().GetScalarRange()[0]
        # if reslice := vtk.vtkImageReslice.SafeDownCast(resliceCursorRep[i].GetReslice()):
        #     reslice.SetBackgroundColor(minVal, minVal, minVal, minVal)

        resliceCursorWidget[i].SetDefaultRenderer(ren[i])
        resliceCursorWidget[i].SetEnabled(1)
        ren[i].GetActiveCamera().SetFocalPoint(0, 0, 0)
        camPos = [0, 0, 0]
        camPos[i] = 1
        ren[i].GetActiveCamera().SetPosition(camPos)
        ren[i].GetActiveCamera().ParallelProjectionOn()
        # bonus
        ren[i].GetActiveCamera().SetViewUp(viewUp[i][0], viewUp[i][1], viewUp[i][2])
        ren[i].ResetCamera()
        cbk.IPW[i] = planeWidget[i]
        cbk.RCW[i] = resliceCursorWidget[i]
        resliceCursorWidget[i].AddObserver(vtk.vtkResliceCursorWidget.ResliceAxesChangedEvent, cbk.Execute)

        # bonus
        rangeVals = [0.0, 0.0]
        reader.GetOutput().GetScalarRange(rangeVals)

        resliceCursorRep[i].SetWindowLevel(rangeVals[1] - rangeVals[0], (rangeVals[0] + rangeVals[1]) / 2.0)
        planeWidget[i].SetWindowLevel(rangeVals[1] - rangeVals[0], (rangeVals[0] + rangeVals[1]) / 2.0)
        resliceCursorRep[i].SetLookupTable(resliceCursorRep[0].GetLookupTable())
        planeWidget[i].GetColorMap().SetLookupTable(resliceCursorRep[0].GetLookupTable())
    
    ren[0].SetBackground(0.3, 0.1, 0.1)
    ren[1].SetBackground(0.1, 0.3, 0.1)
    ren[2].SetBackground(0.1, 0.1, 0.3)
    # outlineActor.GetProperty().SetLineWidth(20)

    # start wrap
    v16 = vtk.vtkDICOMImageReader()
    v16.SetDirectoryName(r"C:\Users\lalal\Desktop\imageProcessing\demo\manifest-1701814559353\QIN LUNG CT\QIN-LSC-0009\09-13-2000-1-CT Thorax wCont-24434\7.000000-RENAL VEN.  3.0  B30f-45454")

    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetInputConnection(v16.GetOutputPort())
    volumeMapper.SetBlendModeToAdditive()
    

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
    ren[3].AddActor(volume)
    # end wrap

    ren[3].SetBackground(0.1, 0.1, 0.1)
    renWin.SetSize(600, 600)

    ren[0].SetViewport(0, 0, 0.5, 0.5)  
    ren[1].SetViewport(0.5, 0, 1, 0.5)
    ren[2].SetViewport(0, 0.5, 0.5, 1)
    ren[3].SetViewport(0.5, 0.5, 1, 1)
    
    ren[3].GetActiveCamera().Elevation(110)
    ren[3].GetActiveCamera().SetViewUp(0, 0, -1)
    ren[3].GetActiveCamera().Azimuth(45)
    ren[3].GetActiveCamera().Dolly(1.15)
    ren[3].ResetCamera()

    renWin.Render()
    iren.Start()

if __name__ == "__main__":
    main()
