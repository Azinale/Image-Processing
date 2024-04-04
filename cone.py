import vtk

# Tạo một đối tượng vtkLineSource để tạo đường
lineSource = vtk.vtkLineSource()
lineSource.SetPoint1(0, 0, 0)  # Đặt điểm bắt đầu của đường
lineSource.SetPoint2(100, 100, 100)  # Đặt điểm kết thúc của đường

# Tạo một mapper và một actor để hiển thị đường
lineMapper = vtk.vtkPolyDataMapper()
lineMapper.SetInputConnection(lineSource.GetOutputPort())

lineActor = vtk.vtkActor()
lineActor.SetMapper(lineMapper)

# Tạo một renderer, một render window, và một render window interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Thêm đối tượng actor vào renderer
renderer.AddActor(lineActor)
renderer.SetBackground(1, 1, 1)  # Đặt màu nền của renderer

# Render và bắt đầu vòng lặp render window interactor
renderWindow.Render()
renderWindowInteractor.Start()
