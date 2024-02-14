import logging
from PIL import Image
from io import BytesIO
from time import sleep
from picamera import PiCamera
from picamera import PiCameraError

class CameraInterface:
    def __init__(self):
        self._camera = None
        try:
            logging.debug("Initializing camera interface")
            self._camera = PiCamera()
            sleep(2)  # Camera warm-up time
            logging.info("Camera initialized successfully")
        except PiCameraError as e:
            logging.error(f"Unable to initialize the camera: {e}")

    def __del__(self):
        self.close()

    def close(self):
        if self._camera is not None:
            try:
                self._camera.close()
                logging.info("Camera resource released successfully")
                self._camera = None
            except Exception as e:
                logging.error(f"An error occurred while closing the camera: {e}")

    def turn_on(self):
        if self._camera is not None:
            try:
                logging.debug("Turning camera on.")
                self._camera.start_preview()
            except Exception as e:
                logging.error(f"Failed to start camera preview: {e}")

    def turn_off(self):
        if self._camera is not None:
            try:
                logging.debug("Turning camera off.")
                self._camera.stop_preview()
            except Exception as e:
                logging.error(f"Failed to stop camera preview: {e}")

                                      
                             
    def capture_image(self, file_path):
        """Capture an image and save it to the specified filename."""
        if self._camera is not None:
            try:
                sleep(2) 
                logging.debug(f"Capturing image to {file_path}")
                self._camera.capture(file_path)
                logging.info(f"Image captured and saved to {file_path}")
            except Exception as e:
                logging.error(f"Failed to capture image: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    camera_interface = CameraInterface()

    camera_interface.turn_on()
    camera_interface.capture_image('FilePath')
    
    camera_interface.turn_off()

    del camera_interface