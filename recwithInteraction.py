import vtk
import itk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk

image1 = itk.imread('Data/case6_gre1.nrrd', itk.F)
image2 = itk.imread('Data/case6_gre2.nrrd', itk.F)

moving_image = image1
fixed_image = image2

TransformType = itk.Euler3DTransform[itk.D]
OptimizerType = itk.RegularStepGradientDescentOptimizerv4[itk.D]
MetricType = itk.MeanSquaresImageToImageMetricv4[fixed_image, moving_image]
RegistrationType = itk.ImageRegistrationMethodv4[fixed_image, moving_image]

transform = TransformType.New()
optimizer = OptimizerType.New()
metric = MetricType.New()
registration = RegistrationType.New()

registration.SetMetric(metric)
registration.SetOptimizer(optimizer)
registration.SetInitialTransform(transform)
registration.SetFixedImage(fixed_image)
registration.SetMovingImage(moving_image)

optimizer.SetLearningRate(4.0)
optimizer.SetMinimumStepLength(0.01)
optimizer.SetNumberOfIterations(200)

registration.Update()

resampler = itk.ResampleImageFilter.New(Input=moving_image, Transform=registration.GetTransform(), UseReferenceImage=True, ReferenceImage=fixed_image)
resampler.SetInterpolator(itk.LinearInterpolateImageFunction.New(fixed_image))
resampler.Update()

output_image = resampler.GetOutput()

np_array = itk.array_from_image(output_image)
vtk_data_array = numpy_to_vtk(np_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
vtk_image = vtk.vtkImageData()
vtk_image.SetDimensions(output_image.GetLargestPossibleRegion().GetSize())
vtk_image.SetOrigin(output_image.GetOrigin())
vtk_image.SetSpacing(output_image.GetSpacing())
vtk_image.GetPointData().SetScalars(vtk_data_array)

reslice = vtk.vtkImageReslice()
reslice.SetInputData(vtk_image)
reslice.SetOutputDimensionality(2)
reslice.SetInterpolationModeToLinear()

matrix = vtk.vtkMatrix4x4()
reslice.SetResliceAxes(matrix)

table = vtk.vtkLookupTable()
table.SetRange(np.min(np_array), np.max(np_array))
table.SetValueRange(0.0, 1.0)
table.SetSaturationRange(0.0, 0.0)
table.SetRampToLinear()
table.Build()

color = vtk.vtkImageMapToColors()
color.SetLookupTable(table)
color.SetInputConnection(reslice.GetOutputPort())

actor_resliced = vtk.vtkImageActor()
actor_resliced.GetMapper().SetInputConnection(color.GetOutputPort())

renderer_resliced = vtk.vtkRenderer()
renderer_resliced.AddActor(actor_resliced)
renderer_resliced.ResetCamera()

window_resliced = vtk.vtkRenderWindow()
window_resliced.AddRenderer(renderer_resliced)
window_resliced.SetWindowName("Image Recalage")

interactorStyle = vtk.vtkInteractorStyleImage()
interactor_resliced = vtk.vtkRenderWindowInteractor()
interactor_resliced.SetInteractorStyle(interactorStyle)
window_resliced.SetInteractor(interactor_resliced)

actions = {"Slicing": 0}

def ButtonCallback(obj, event):
    if event == "LeftButtonPressEvent":
        actions["Slicing"] = 1
    else:
        actions["Slicing"] = 0

def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor_resliced.GetLastEventPosition()
    (mouseX, mouseY) = interactor_resliced.GetEventPosition()
    if actions["Slicing"] == 1:
        deltaY = mouseY - lastY
        reslice.Update()
        sliceSpacing = reslice.GetOutput().GetSpacing()[2]
        matrix = reslice.GetResliceAxes()
        center = matrix.MultiplyPoint((0, 0, sliceSpacing * deltaY, 1))
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        reslice.SetResliceAxes(matrix)
        window_resliced.Render()
    else:
        interactorStyle.OnMouseMove()

interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)

window_resliced.Render()
interactor_resliced.Initialize()
interactor_resliced.Start()

del renderer_resliced
del window_resliced
del interactor_resliced
