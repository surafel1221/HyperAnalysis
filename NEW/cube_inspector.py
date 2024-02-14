"""

This file contains the CubeInspector class for showing scanned spectral cube and
the smile corrected versions of it.

False color calculations and spectral angle mapping are kept outside of the class
in case they are to be used with synthetic data at some point.

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import logging



def calculate_false_color_images(np_cube_list, spectral_blue, spectral_green, spectral_red):
    """
    Calculate false color images for each cube in the list.
    
    Parameters:
    np_cube_list (list of numpy arrays): List of 3D cubes (height x width x spectral bands).
    spectral_blue (int): Index of blue band in the cube.
    spectral_green (int): Index of green band in the cube.
    spectral_red (int): Index of red band in the cube.

    Returns:
    list of numpy arrays: False color images for each cube.
    """

    false_list = []
    for cube in np_cube_list:
        
        blue_band = cube[:, :, spectral_blue]
        green_band = cube[:, :, spectral_green]
        red_band = cube[:, :, spectral_red]

       
        false_color_image = np.stack((red_band, green_band, blue_band), axis=-1)
        false_color_image = false_color_image / np.max(false_color_image, axis=(0, 1), keepdims=True)

        false_list.append(false_color_image.clip(min=0.0, max=1.0)) 

    return false_list


def calculate_sam(source_cube, sam_window_start, sam_window_end, sam_ref_x,
                  use_radians=False, spectral_filter=None, use_scm=False):
 

    # Define the slices for the window and spectral filter
    y_slice = slice(sam_window_start[0], sam_window_end[0])
    x_slice = slice(sam_window_start[1], sam_window_end[1])
    spectral_filter = spectral_filter if spectral_filter is not None else slice(None, None)

    # Clip the reference x-coordinate to be within the window
    cos_ref = np.clip(sam_ref_x, sam_window_start[1], sam_window_end[1])

    # Extract the reference spectrum and the cube subset
    reference_spectrum = source_cube[sam_window_start[0]:sam_window_end[0], cos_ref, spectral_filter].mean(axis=0)
    cube_subset = source_cube[y_slice, x_slice, spectral_filter]

    # Compute the dot product or correlation
    if not use_scm:
        # Normalize the spectra
        reference_norm = np.linalg.norm(reference_spectrum)
        cube_norm = np.linalg.norm(cube_subset, axis=2, keepdims=True)
        
        dot_product = np.einsum('i,jki->jk', reference_spectrum, cube_subset) / (reference_norm * cube_norm)
    else:
        reference_centered = reference_spectrum - reference_spectrum.mean()
        cube_centered = cube_subset - cube_subset.mean(axis=2, keepdims=True)
        
        dot_product = np.einsum('i,jki->jk', reference_centered, cube_centered) / (np.linalg.norm(reference_centered) * np.linalg.norm(cube_centered, axis=2))

    dot_product = np.clip(dot_product, -1, 1)

    if use_radians:
        sam = np.arccos(dot_product)
    else:
        sam = dot_product

    sam_image = np.zeros(source_cube.shape[:2], dtype=np.float64)
    sam_image[y_slice, x_slice] = sam

    return sam_image, sam

class CubeInspector:
    """
    CubeInspector class for showing scanned spectral cube and the smile corrected versions of it.

    CubeInspector is an interactive matplotlib-based inspector program with simple key and mouse commands.
    """

    def __init__(self, org, lut=None, intr=None):
        # Store the cubes in a list. Order is org, lut, intr if present
        self.cubes = [cube for cube in [org, lut, intr] if cube is not None]
        
        self.false_color_images = [] 



        if len(self.cubes) == 0:
            raise ValueError("At least one cube must be provided.")

        self.row_count = 1 if len(self.cubes) <= 1 else 2

        # Assuming the data is structured as (height, width, spectral bands)
        self.width_image = self.cubes[0].shape[1]
        self.height_image = self.cubes[0].shape[0]

        # Initialize midpoints for y (height), x (width), and spectral band
        self.idx = int(self.height_image / 2)
        self.y = int(self.width_image / 2)
        self.x = int(self.cubes[0].shape[2] / 2)

        # Modes: 1 for reflectance image, 2 for false color image, 3 for spectral angle
        self.mode = 1

        # False color images calculated lazily only once.
        self.false_color_calculated = False

        # Matplotlib figure and axis.
        self.fig = None
        self.ax = None
        # First call to show() will initialize plots.
        self.plot_inited = False

        # Color palettes.
        self.colors_org_lut_intr = ['black', 'lightcoral', 'purple']
        self.color_pixel_selection = 'violet'

        # Images to be plotted on update. Active mode will stuff images in 
        # this list, which are then drawn over the old ones.
        self.images = []
        
        # Stores cosine maps (org, lut, intr) of the selected area.
        self.sam_chunks_list = []

        # Image overlay decorations. Store handles for removing the objects.
        self.decorations_selection = []
        self.decorations_box = []

        self.connection_mouse = None
        self.connection_button = None

    def init_plot(self):
     """Initialize the plots and connect mouse and keyboard."""
     self.fig, temp_ax = plt.subplots(nrows=self.row_count, ncols=2, num='Cube', figsize=(16, 12))
     self.ax = np.array([[temp_ax[0], temp_ax[1]]]) if self.row_count == 1 else np.array([[temp_ax[0, 0], temp_ax[0, 1]], [temp_ax[1, 0], temp_ax[1, 1]]])
     self.connect_ui()
     for i, cube in enumerate(self.cubes):
        n, m = divmod(i, 2)
        # Corrected line: Direct indexing for numpy arrays
        ax_image = self.ax[n, m].imshow(cube[:, :, self.x], origin='lower')
        self.images.append(ax_image)
     self.plot_inited = True


        
  

   

    

    def nth_image_as_index(self, n):
        if n == 1:
            return 0,1
        if n == 2:
            return 1,1
        if n == 3:
            return 1,0
        return 0,0

    def init_plot(self):
     """Initialize the plots and connect mouse and keyboard."""
     self.fig, temp_ax = plt.subplots(nrows=self.row_count, ncols=2, num='Cube', figsize=(16, 12))
     self.ax = np.array([[temp_ax[0], temp_ax[1]]]) if self.row_count == 1 else np.array([[temp_ax[0, 0], temp_ax[0, 1]], [temp_ax[1, 0], temp_ax[1, 1]]])
     self.connect_ui()
     for i, cube in enumerate(self.cubes):
        n, m = divmod(i, 2)
        ax_image = self.ax[n, m].imshow(cube[:, :, self.x], origin='lower')  # Changed line
        self.images.append(ax_image)
     self.plot_inited = True

    def connect_ui(self):
        """Connect mouse and keyboard."""

        self.connection_mouse = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.connection_button = self.fig.canvas.mpl_connect('key_press_event', self.keypress)

    def disconnect_ui(self):
        """Disconnect mouse and keyboard."""

        self.fig.canvas.mpl_disconnect(self.connection_mouse)
        self.fig.canvas.mpl_disconnect(self.connection_button)

    def onclick(self, event):
        """ Handle mouse clicks.

        Usage
        -----
            alt + click
                Ignores the click. Allows using matplotlib's own commands 
                such as zooming without interference.
            shift + click
                First time: set the starting corner of a cosine box, second click 
                finishes the selection and triggers image update. Any other click 
                between these two will reset the selection.
            click on line plot area in mode 1
                Select new band and trigger image update.
            click on any image in modes 1 or 2
                Select new pixel to plot spectra for.
            click on any image in mode 3
                Select new reference point for cosine angle calculations.
        """

        if event.key == 'alt':
            return
        if event.inaxes is not None:
            # Clicking line plot triggers band change in mode 1
            if event.inaxes is self.ax[0,0] and self.mode == 1:
                self.show(band=int(event.xdata))
            # Clicking one of the three images..
            else:
                # Shift clicks set boxes for cosine calculations.
                if event.key == 'shift':
                    # First shift click selects first corner of cos box
                    if not self.sam_window_corner_given:
                        self.sam_window_start_sug = [int(event.xdata), int(event.ydata)]
                        self.sam_window_corner_given = True
                    # Second click finalizes the box and triggers an update.
                    else:
                        startX = self.sam_window_start_sug[0]
                        startY = self.sam_window_start_sug[1]
                        x = int(event.xdata)
                        y = int(event.ydata)
                        if x < startX:
                            temp = x
                            x = startX
                            startX = temp
                        if y < startY:
                            temp = y
                            y = startY
                            startY = temp
                        self.sam_window_start = [startX, startY]
                        self.sam_window_end = [x, y]
                        # reset status
                        self.sam_window_corner_given = False
                        self.sam_window_start_sug = [startX, startY]
                        # If in cosmap mode, force update in show()
                        if self.mode == 3:
                            # Update cos box without updating the reference point
                            self.show(force_update=True)
                else:
                    # any other update command resets cos box status
                    self.sam_window_corner_given = False
                    self.sam_window_start_sug = [self.sam_window_start[0], self.sam_window_start[1]]
                    if self.mode == 3:
                        self.show(sam_ref_x=int(event.xdata))
                    else:
                        self.show(x=int(event.xdata), y=int(event.ydata))

    def keypress(self, event):
        """ Handles key presses.

        Usage
        -----
            numkey 1
                Select reflectance image mode.
            numkey 2
                Select false color image mode.
            numkey 3
                Select cosine angle mode.
            r
                Toggle between dot product and cosine angle in mode 3.
            a
                If in mode 3, move spectral filter to the left
            d
                If in mode 3, move spectral filter to the right
        """

        key = event.key
        if key == '1' or key == '2' or key == '3':
            self.mode = int(key)
            self.show(mode=self.mode)
        if key == 'r':
            self.toggle_radians = not self.toggle_radians
            self.show(force_update=True)
        if self.mode == 3:      # How much the spectral filter is moved to left or right.            
            if key == 'a':      
                low = self.spectral_filter.start - self.spectral_filter_step
                high = self.spectral_filter.stop - self.spectral_filter_step
                low = np.clip(low, a_min=0, a_max=self.spectral_filter_max)
                high = np.clip(high, a_min=0, a_max=self.spectral_filter_max)
                self.spectral_filter = slice(low, high)
                self.show(force_update=True)        
            if key == 'd':      
                low = self.spectral_filter.start + self.spectral_filter_step
                high = self.spectral_filter.stop + self.spectral_filter_step
                low = np.clip(low, a_min=0, a_max=self.spectral_filter_max)
                high = np.clip(high, a_min=0, a_max=self.spectral_filter_max)
                self.spectral_filter = slice(low, high)
                self.show(force_update=True)
            if key == 'u':
                self.reload_control()
                self.reinit_spectral_filter()
                self.reinit_false_color_spectra()
                self.show(force_update=True)
    
    def show(self, x=None, y=None, band=None, force_update=False, sam_ref_x=None):
        """Update images, spectrograms, and overlays as needed."""
        band_changed = False

        if x is not None:
            self.y = x
        if y is not None:
            self.idx = y
        if band is not None:
            self.x = band
            band_changed = True

        if not self.plot_inited:
            self.init_plot()
            force_update = True

        # Update images whenever needed
        if band_changed or force_update:
            self.update_images()

        plt.show()
        plt.draw()
    def update_images(self):
        """Updates images to display them in grayscale for the specified band."""
        for i, cube in enumerate(self.cubes):
            # Display the grayscale image for the specified band
            grayscale_data = cube[:, :, self.x]
            self.images[i].set_data(grayscale_data)
            self.images[i].set_cmap('gray')
            self.images[i].set_clim(vmin=grayscale_data.min(), vmax=grayscale_data.max())

            # Display false color image on the right-side plot
            if i < len(self.false_color_images):
                n, m = self.nth_image_as_index(i)
                self.ax[n, m+1].imshow(self.false_color_images[i])  
                self.ax[n, m+1].set_title(f'False Color')

            # Update titles if needed
            titles = ['ORG Grayscale', 'LUT Grayscale', 'INTR Grayscale']
            for j, ax in enumerate(self.ax.flat):
                if j < len(self.images):
                    ax.set_title(f'{titles[j]}, band={self.x}')
        plt.draw()
    def update_spectrograms(self):
     """Update spectrogram view (top left) and its overlays."""

     self.ax[0, 0].clear()
     if self.mode == 1 or self.mode == 2:
        for i, cube in enumerate(self.cubes):
            # Extracting spectral data for the selected pixel
            spectral_data = cube[self.idx, self.y, :]
            self.ax[0, 0].plot(spectral_data, color=self.colors_org_lut_intr[i])

        self.ax[0, 0].set_title('Spectrograms')
        self.ax[0, 0].set_xlabel('Spectral Band')
        self.ax[0, 0].set_ylabel('Intensity')

        # Redraw band selection indicator if in mode 1 (reflectance image mode)
        if self.mode == 1:
            _, ylim = self.ax[0, 0].get_ylim()
            self.ax[0, 0].vlines(self.x, ylim[0], ylim[1], color=self.color_pixel_selection)

     elif self.mode == 3:
        # Implement spectral angle maps if needed
        pass
       

     plt.draw()

    

    def calculate_sams(self):
        """Calculates and saves spectral angle maps for all three cubes and sets them to image list."""

        sams = []
        self.sam_chunks_list = []
        for i,cube in enumerate(self.cubes):
            sam, cosMapChunk = calculate_sam(cube, self.sam_window_start, self.sam_window_end,
                                             self.sam_ref_x, self.viewable, self.toggle_radians, self.spectral_filter)
            sams.append(sam)
            self.sam_chunks_list.append(cosMapChunk)

        maxVal = np.max(np.array(list(np.max(chunk) for chunk in self.sam_chunks_list)))

        for i,sam in enumerate(sams):
            self.images[i].set_data(sam)
            self.images[i].set_norm(cm.colors.Normalize(sam.min(), maxVal))