import tkinter as tk
from camera_interface import CameraInterface
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from cube_inspector import CubeInspector
from cube_inspector import calculate_false_color_images
import logging

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI App")

        # Create CameraInterface instance
        self.camera_interface = CameraInterface()

        # Create CubeInspector instance
        self.cube_inspector = None

        # Create GUI buttons
        self.capture_btn = tk.Button(root, text="Capture Image", command=self.capture_image)
        self.capture_btn.pack()

        self.display_cube_btn = tk.Button(root, text="Display Cube", command=self.display_cube)
        self.display_cube_btn.pack()

       

    def capture_image(self):
        self.camera_interface.turn_on()
        self.camera_interface.capture_image('captured_image.jpg')
        self.camera_interface.turn_off()
        logging.info("Image captured and saved")

    def display_cube(self):
        mat_file_path = 'indian_pines.mat'
        data = loadmat(mat_file_path)
        if 'indian_pines' in data:
            hyperspectral_data = data['indian_pines']
            spectral_blue = 38  
            spectral_green = 29  
            spectral_red = 89
            false_color_images = calculate_false_color_images([hyperspectral_data], spectral_blue, spectral_green, spectral_red)
            self.cube_inspector = CubeInspector(org=hyperspectral_data)
            self.cube_inspector.false_color_images = false_color_images
            self.cube_inspector.show()
        else:
            logging.error("Key 'indian_pines' not found in the .mat file.")

   

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    app = App(root)
    root.mainloop()