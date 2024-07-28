import vtk

reader = vtk.vtkNrrdReader()
reader.SetFileName('Data/case6_gre1.nrrd')
reader.Update()

reader2 = vtk.vtkNrrdReader()
reader2.SetFileName('Data/case6_gre2.nrrd')
reader2.Update()

(xMin, xMax, yMin, yMax, zMin, zMax) = reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
(xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
(x0, y0, z0) = reader.GetOutput().GetOrigin()

center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (zMin + zMax)]

(xMin2, xMax2, yMin2, yMax2, zMin2, zMax2) = reader2.GetExecutive().GetWholeExtent(reader2.GetOutputInformation(0))
(xSpacing2, ySpacing2, zSpacing2) = reader2.GetOutput().GetSpacing()
(x02, y02, z02) = reader2.GetOutput().GetOrigin()

center2 = [x02 + xSpacing2 * 0.5 * (xMin2 + xMax2),
           y02 + ySpacing2 * 0.5 * (yMin2 + yMax2),
           z02 + zSpacing2 * 0.5 * (zMin2 + zMax2)]

coronal = vtk.vtkMatrix4x4()
coronal.DeepCopy((1, 0, 0, center[0],
                  0, 0, 1, center[1],
                  0, -1, 0, center[2],
                  0, 0, 0, 1))

axial2 = vtk.vtkMatrix4x4()
axial2.DeepCopy((1, 0, 0, center2[0],
                 0, 1, 0, center2[1],
                 0, 0, 1, center2[2],
                 0, 0, 0, 1))

reslice = vtk.vtkImageReslice()
reslice.SetInputConnection(reader.GetOutputPort())
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(coronal)
reslice.SetInterpolationModeToLinear()

reslice2 = vtk.vtkImageReslice()
reslice2.SetInputConnection(reader2.GetOutputPort())
reslice2.SetOutputDimensionality(2)
reslice2.SetResliceAxes(axial2)
reslice2.SetInterpolationModeToLinear()

table = vtk.vtkLookupTable()
table.SetRange(300, 2000)  
table.SetValueRange(0.0, 1.0)  
table.SetSaturationRange(0.0, 0.0)  
table.SetRampToLinear()
table.Build()

table2 = vtk.vtkLookupTable()
table2.SetRange(300, 2000) 
table2.SetValueRange(0.0, 1.0)  
table2.SetSaturationRange(0.0, 0.0) 
table2.SetRampToLinear()
table2.Build()

color = vtk.vtkImageMapToColors()
color.SetLookupTable(table)
color.SetInputConnection(reslice.GetOutputPort())

color2 = vtk.vtkImageMapToColors()
color2.SetLookupTable(table2)
color2.SetInputConnection(reslice2.GetOutputPort())

actor = vtk.vtkImageActor()
actor.GetMapper().SetInputConnection(color.GetOutputPort())

actor2 = vtk.vtkImageActor()
actor2.GetMapper().SetInputConnection(color2.GetOutputPort())

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)

renderer2 = vtk.vtkRenderer()
renderer2.AddActor(actor2)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetWindowName("gre1")

window2 = vtk.vtkRenderWindow()
window2.AddRenderer(renderer2)
window2.SetWindowName("gre2")

interactorStyle = vtk.vtkInteractorStyleImage()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
window.SetInteractor(interactor)

interactorStyle2 = vtk.vtkInteractorStyleImage()
interactor2 = vtk.vtkRenderWindowInteractor()
interactor2.SetInteractorStyle(interactorStyle2)
window2.SetInteractor(interactor2)

actions = {"Slicing": 0}

def ButtonCallback(obj, event):
    if event == "LeftButtonPressEvent":
        actions["Slicing"] = 1
    else:
        actions["Slicing"] = 0

def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 1:
        deltaY = mouseY - lastY
        reslice.Update()
        sliceSpacing = reslice.GetOutput().GetSpacing()[2]
        matrix = reslice.GetResliceAxes()
        center = matrix.MultiplyPoint((0, 0, sliceSpacing * deltaY, 1))
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        window.Render()
    else:
        interactorStyle.OnMouseMove()

def MouseMoveCallback2(obj, event):
    (lastX, lastY) = interactor2.GetLastEventPosition()
    (mouseX, mouseY) = interactor2.GetEventPosition()
    if actions["Slicing"] == 1:
        deltaY = mouseY - lastY
        reslice2.Update()
        sliceSpacing = reslice2.GetOutput().GetSpacing()[2]
        matrix = reslice2.GetResliceAxes()
        center = matrix.MultiplyPoint((0, 0, sliceSpacing * deltaY, 1))
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        window2.Render()
    else:
        interactorStyle2.OnMouseMove()

interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)

interactorStyle2.AddObserver("MouseMoveEvent", MouseMoveCallback2)
interactorStyle2.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle2.AddObserver("LeftButtonReleaseEvent", ButtonCallback)

window.Render()
interactor.Initialize()

window2.Render()
interactor2.Initialize()

interactor.Start()
interactor2.Start()

del renderer
del window
del interactor
del renderer2
del window2
del interactor2
