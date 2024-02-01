
from core.camera_interface import CameraInterface

import logging
from xarray import DataArray

def main():
    logging.basicConfig(level=logging.INFO)  # Configure logging
    
    # Initialize the camera interface
    camera_interface = CameraInterface()
    
    # Test capturing a single frame
    single_frame = camera_interface.get_frame()
    if isinstance(single_frame, DataArray):
        logging.info("Successfully captured a single frame.")
    else:
        logging.error("Failed to capture a single frame.")
    
    # Test capturing a frame using the optimized method
    optimized_frame = camera_interface.get_frame_opt(count=3, method='mean')
    if isinstance(optimized_frame, DataArray):
        logging.info("Successfully captured a frame using the optimized method.")
    else:
        logging.error("Failed to capture a frame using the optimized method.")
    
    # Test setting and getting camera features
    try:
        # Set exposure
        test_exposure_value = 10000  # example value in microseconds
        camera_interface.exposure(test_exposure_value)
        current_exposure = camera_interface.exposure()
        logging.info(f"Exposure set and get test passed. Current exposure: {current_exposure} microseconds.")
        
        # Set gain
        test_gain_value = 1.5  # example value
        camera_interface.gain(test_gain_value)
        current_gain = camera_interface.gain()
        logging.info(f"Gain set and get test passed. Current gain: {current_gain}.")
        
        # Set cropping (simulated by zoom in PiCamera)
        camera_interface.crop(x=0.2, y=0.2, width=0.6, height=0.6)
        logging.info("Crop (zoom) set test passed.")
        
    except Exception as e:
        logging.error(f"An error occurred while testing camera features: {e}")
    
    # Test turning camera preview on and off
    try:
        camera_interface.turn_on()
        logging.info("Camera preview turned on.")
        camera_interface.turn_off()
        logging.info("Camera preview turned off.")
    except Exception as e:
        logging.error(f"An error occurred while turning camera preview on/off: {e}")
    
    # Close the camera interface
    camera_interface.close()
    logging.info("Camera interface closed successfully.")

if __name__ == "__main__":
    main()