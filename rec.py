import vtk
import itk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk

image1 = itk.imread('Data/case6_gre1.nrrd', itk.F)
image2 = itk.imread('Data/case6_gre2.nrrd', itk.F)

moving_image = image1
fixed_image= image2

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

actor_resampled = vtk.vtkImageActor()
actor_resampled.GetMapper().SetInputData(vtk_image)

renderer_resampled = vtk.vtkRenderer()
renderer_resampled.AddActor(actor_resampled)

window_resampled = vtk.vtkRenderWindow()
window_resampled.AddRenderer(renderer_resampled)       
window_resampled.SetWindowName("image recaler")
window_resampled.Render()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window_resampled)
interactor.Start()

