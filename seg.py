import itk
import numpy as np
import matplotlib.pyplot as plt

def normalize(img):
    min_val = np.min(img)
    max_val = np.max(img)
    normalized = 255 * (img - min_val) / (max_val - min_val)
    return normalized

def segmentation(image,seedX,seedY,low_threshold,high_treshold):
    img_array = normalize(image)
    img = itk.image_from_array(img_array)
    

    smoother = itk.GradientAnisotropicDiffusionImageFilter.New(Input=img, NumberOfIterations=20, TimeStep=0.04,
                                                            ConductanceParameter=3)

    smoother.Update()

    connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother.GetOutput())
    connected_threshold.SetReplaceValue(255)
    connected_threshold.SetLower(low_threshold)
    connected_threshold.SetUpper(high_treshold)
    
    connected_threshold.SetSeed((seedX, seedY))
    connected_threshold.Update()

    return itk.array_from_image(connected_threshold.GetOutput())


def main():
    image1 = itk.imread('Data/case6_gre1.nrrd', itk.F)
    image2 = itk.imread('Data/case6_gre2.nrrd', itk.F)

    array1= itk.array_from_image(image1)
    array2= itk.array_from_image(image2)

    temp1 = []
    for i in range(len(array1)):
        x = segmentation(array1[i], 
                    seedX = 125,
                    seedY = 65,
                    low_threshold= 110.,
                    high_treshold=150.)
        temp1.append(x)

    new_img1 = itk.image_from_array(temp1)
    itk.imwrite(new_img1, "segmentation_case6_gre1.nrrd")

    temp2 = []
    for i in range(len(array2)):
        x = segmentation(array2[i], 
                    seedX = 125,
                    seedY = 80,
                    low_threshold= 110.,
                    high_treshold=170.)
        temp2.append(x)

    new_img2 = itk.image_from_array(temp2)
    itk.imwrite(new_img2, "segmentation_case6_gre2.nrrd")

if __name__ == "__main__":
    main()