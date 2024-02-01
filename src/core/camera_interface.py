

import logging
import xarray as xr
from xarray import DataArray
import os

from core import properties as P
from utilities import numeric as N
from PIL import Image
from io import BytesIO
import numpy as np
from xarray import DataArray
from time import sleep
from picamera import PiCamera
from picamera import PiCameraError



_camera=None
class CameraInterface:
    def __init__(self):
        """Initialize the Raspberry Pi Camera."""
        try:
            logging.debug("Initializing camera interface")
            self._camera = PiCamera()
            sleep(2)  # Camera warm-up time
            logging.info("Camera initialized successfully")
        except PiCameraError as e:
            logging.error(f"Unable to initialize the camera: {e}")
            self._camera = None


def __del__(self):
    self.close()
 
def close(self):
        """Stop preview """
        if self._camera is not None:
            try:
                self._camera.close()
                logging.info("Camera resource released successfully")
                self._camera = None
            except Exception as e:
                logging.error(f"An error occurred while closing the camera: {e}")

def turn_on(self):
        """Start camera preview."""
        if self._camera is not None:
            try:
                logging.debug("Turning camera on.")
                self._camera.start_preview()
            except Exception as e:
                logging.error(f"Failed to start camera preview: {e}")
                
def turn_off(self):
        """Stop camera preview."""
        if self._camera is not None:
            try:
                logging.debug("Turning camera off.")
                self._camera.stop_preview()
            except Exception as e:
                logging.error(f"Failed to stop camera preview: {e}") 


def get_frame(self) -> DataArray:
    """Capture a frame using the PiCamera library and return it as a DataArray."""
    if self._camera is not None:
        try:
            logging.debug("Capturing image")
            
            # Capture an image using PiCamera
            stream = BytesIO()
            self._camera.capture(stream, format='jpeg')
            stream.seek(0)
            
            # Convert the captured image to a DataArray
            image = Image.open(stream)
            image_array = np.array(image)
            data_array = DataArray(image_array)
            
            logging.info("Image captured successfully")
            return data_array
        except Exception as e:
            logging.error(f"Failed to capture image: {e}")
    
    return None 


def get_frame_opt(self, count=1, method='mean') -> DataArray:
    """Acquire a frame which is a mean or median of several frames.
    
    Camera state (acquiring or not) will be preserved.

    Parameters
    ----------
    count : int, default=1
        If given, the mean of 'mean' consecutive frames is returned. If count == 1
        this is the same as get_frame().
    method: str, default = 'mean'
        Either 'mean' or 'median' of count consecutive frames.

    Returns
    -------
    frame : DataArray
        The shot frame.
    """
    
    if self._camera is not None:
        try:
            # Check if the camera is currently previewing
            camera_was_acquiring = self._camera.previewing
            if not camera_was_acquiring:
                self._camera.start_preview()
            
            frames = []
            for _ in range(count):
                stream = BytesIO()
                self._camera.capture(stream, format='jpeg')
                stream.seek(0)
                image = Image.open(stream)
                image_array = np.array(image)
                frames.append(DataArray(image_array))
            
            frame = xr.concat(frames, dim='timestamp')
            
            if method == 'mean':
                frame = frame.mean(dim='timestamp')
            elif method == 'median':
                frame = frame.median(dim='timestamp')
            else:
                logging.error(f"Shooting method '{method}' not recognized. Use either 'mean' or 'median'.")
            
            # Stop the preview if it wasn't previewing before the function call
            if not camera_was_acquiring:
                self._camera.stop_preview()
            
            return frame
        except Exception as e:
            logging.error(f"Failed to acquire frames: {e}")
    
    return None


def exposure(self, value=None):
        """Set or print exposure"""
        if value is None:
            return self._camera.exposure_speed
        else:
            self._camera.exposure_mode = 'off'  # Disable automatic exposure
            self._camera.shutter_speed = value  # Set the exposure time in microseconds


def _set_camera_feature(self, name, val):
 """Change camera settings.

        Note: OutOfRangeException related to features with certain increment
        (e.g. height, width) throws an exception which cannot be handle here.

        Parameters
        ----------
        name : string
            Name of the feature e.g. 'ExposureTime'
        val :
            Value to be set. Depending on the feature this might
            be int, string, bool etc.
    """
 if name in self._camera:
        camera_was_acquiring = self._camera.recording  # Check if the camera is currently recording

        try:
            # Try to set the value even if live feed is running.
            setattr(self._camera, name, val)
            print(f"Feature '{name}' was successfully set to {val}.")
        except Exception as e:
            logging.error(f"Could not set the feature {name}. Error: {e}")
        finally:
            # If the camera was recording, restart the recording
            if camera_was_acquiring:
                self._camera.start_recording()

 else:
        logging.warning(f"Feature '{name}' is not available in PiCamera.")
 
 
 
 
            
def crop(self, x=0.0, y=0.0, width=1.0, height=1.0):
    """Set camera zoom to simulate cropping.

    Parameters
    ----------
    x : float
        The horizontal position of the zoom area (0.0 to 1.0)
    y : float
        The vertical position of the zoom area (0.0 to 1.0)
    width : float
        The width of the zoom area (0.0 to 1.0)
    height : float
        The height of the zoom area (0.0 to 1.0)
    """
    if self._camera is not None:
        try:
            self._camera.zoom = (x, y, width, height)
            logging.info(f"Zoom area set to {(x, y, width, height)}")
        except Exception as e:
            logging.error(f"Failed to set zoom area: {e}")                                     
                             
        