import scipy.io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


# Load the .mat file
mat_data = scipy.io.loadmat('C:\\Users\\suraf\\Downloads\\HYPERCUBES\\2000_50.mat')
# Print out all of the keys in mat_data dictionary
print(mat_data.keys())
# Extract wavelength information
hyperspectral_Wavelength = mat_data['parameters'][0, 0][4][0]
wavelengths = hyperspectral_Wavelength.flatten()
print("Hyperspectral wavelength: ", hyperspectral_Wavelength)


# Target wavelength
target_wavelength = 927

# Find the index of the band with the closest wavelength to the target
index_band = np.argmin(np.abs(wavelengths - target_wavelength))

print(f"The index of the band with wavelength {target_wavelength} nm is: {index_band}")

# Load hyperspectral cube
hyperspectral_image = mat_data['H']

# Display the selected band
plt.imshow(hyperspectral_image[:, :, index_band], cmap='gray')
plt.title(f'Hyperspectral Cube - Band {index_band} (Wavelength: {wavelengths[index_band]} nm)')
plt.show()

