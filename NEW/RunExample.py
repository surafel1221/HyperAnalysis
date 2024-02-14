import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from cube_inspector import CubeInspector
from cube_inspector import calculate_false_color_images
 

def main():
    # Load .mat file
    mat_file_path = r'C:\Users\suraf\NEW\indian_pines.mat'

    data = loadmat(mat_file_path)
    
    print("Keys in the .mat file:", data.keys())
    
    if 'indian_pines' in data:
        hyperspectral_data = data['indian_pines']
        print("Hyperspectral data loaded successfully.")
        
        print("Type of hyperspectral_data:", type(hyperspectral_data))
        print("Shape of hyperspectral_data:", hyperspectral_data.shape)
        spectral_blue = 38  
        spectral_green = 29  
        spectral_red = 89
        
        false_color_images = calculate_false_color_images([hyperspectral_data], spectral_blue, spectral_green, spectral_red)
        
        cube_inspector = CubeInspector(org=hyperspectral_data, lut=None, intr=None)
        cube_inspector.false_color_images = false_color_images  # Assign false color images to the inspector
        
        cube_inspector.show()
    else:
    
        print("Key 'indian_pines' not found in the .mat file.")
        hyperspectral_data = data['wavelengths']
        print(hyperspectral_data)

if __name__ == "__main__":
    main()

