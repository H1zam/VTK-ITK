import vtk

# Start by loading some data.
reader = vtk.vtkNrrdReader()
reader.SetFileName('Data/case6_gre1.nrrd')
reader.Update()

reader2 = vtk.vtkNrrdReader()
reader2.SetFileName('Data/case6_gre2.nrrd')
reader2.Update()

# Ensure the whole extent is set
information = reader.GetOutputInformation(0)
whole_extent = reader.GetOutput().GetExtent()
information.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(), whole_extent, 6)

information2 = reader2.GetOutputInformation(0)
whole_extent2 = reader2.GetOutput().GetExtent()
information2.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(), whole_extent2, 6)

# Calculate the center of the volume
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

# Matrices for axial, coronal, sagittal, oblique view orientations
axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1, 0, 0, center[0],
                0, 1, 0, center[1],
                0, 0, 1, center[2],
                0, 0, 0, 1))

coronal = vtk.vtkMatrix4x4()
coronal.DeepCopy((1, 0, 0, center[0],
                  0, 0, 1, center[1],
                  0,-1, 0, center[2],
                  0, 0, 0, 1))

sagittal = vtk.vtkMatrix4x4()
sagittal.DeepCopy((0, 0,-1, center[0],
                   1, 0, 0, center[1],
                   0,-1, 0, center[2],
                   0, 0, 0, 1))

oblique = vtk.vtkMatrix4x4()
oblique.DeepCopy((1, 0, 0, center[0],
                  0, 0.866025, -0.5, center[1],
                  0, 0.5, 0.866025, center[2],
                  0, 0, 0, 1))


axial2 = vtk.vtkMatrix4x4()
axial2.DeepCopy((1, 0, 0, center2[0],
                0, 1, 0, center2[1],
                0, 0, 1, center2[2],
                0, 0, 0, 1))

coronal2 = vtk.vtkMatrix4x4()
coronal2.DeepCopy((1, 0, 0, center2[0],
                  0, 0, 1, center2[1],
                  0,-1, 0, center2[2],
                  0, 0, 0, 1))

sagittal2 = vtk.vtkMatrix4x4()
sagittal2.DeepCopy((0, 0,-1, center2[0],
                   1, 0, 0, center2[1],
                   0,-1, 0, center2[2],
                   0, 0, 0, 1))

oblique2 = vtk.vtkMatrix4x4()
oblique2.DeepCopy((1, 0, 0, center2[0],
                  0, 0.866025, -0.5, center2[1],
                  0, 0.5, 0.866025, center2[2],
                  0, 0, 0, 1))



# Extract a slice in the desired orientation
reslice = vtk.vtkImageReslice()
reslice.SetInputConnection(reader.GetOutputPort())
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(axial)
reslice.SetInterpolationModeToLinear()

reslice2 = vtk.vtkImageReslice()
reslice2.SetInputConnection(reader2.GetOutputPort())
reslice2.SetOutputDimensionality(2)
reslice2.SetResliceAxes(axial2)
reslice2.SetInterpolationModeToLinear()


# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(300, 2000) # image intensity range
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0.0) # no color saturation
table.SetRampToLinear()
table.Build()

table2 = vtk.vtkLookupTable()
table2.SetRange(300, 2000) # image intensity range
table2.SetValueRange(0.0, 1.0) # from black to white
table2.SetSaturationRange(0.0, 0.0) # no color saturation
table2.SetRampToLinear()
table2.Build()

# Map the image through the lookup table
color = vtk.vtkImageMapToColors()
color.SetLookupTable(table)
color.SetInputConnection(reslice.GetOutputPort())

color2 = vtk.vtkImageMapToColors()
color2.SetLookupTable(table2)
color2.SetInputConnection(reslice2.GetOutputPort())

# Display the image
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

window2 = vtk.vtkRenderWindow()
window2.AddRenderer(renderer2)


# Set up the interaction
interactorStyle = vtk.vtkInteractorStyleImage()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
window.SetInteractor(interactor)
window.SetWindowName("gre1")
window.Render()

window2.SetWindowName("gre2")
window2.Render()


# Create callbacks for slicing the image
actions = {}
actions["Slicing"] = 0

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
        # move the center point that we are slicing through
        center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        window.Render()
    else:
        interactorStyle.OnMouseMove()

interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)



# Start interaction
interactor.Start()

del renderer
del window
del interactor
del renderer2
del window2
