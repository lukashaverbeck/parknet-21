from typing import Optional

import picamera
import picamera.array
import pyzbar.pyzbar as pyzbar

from util import Singleton

RESOLUTION = (1920, 1080)
BRIGHTNESS = 60


@Singleton
class Scanner:
    def __init__(self):
        self._camera = picamera.PiCamera()
        self._camera.resolution = RESOLUTION
        self._camera.brightness = BRIGHTNESS

    @property
    def _image(self) -> picamera.array.PiRGBArray:
        with self._camera as camera, picamera.array.PiRGBArray(camera) as frame:
            # capture and return image
            camera.capture(frame, "rgb")
            return frame.array

    @property
    def ahead_signature(self) -> Optional[str]:
        # get QR object from camera image
        decoded_objects = pyzbar.decode(self._image)

        # check if any QR codes have been found
        if len(decoded_objects) > 0:
            # decode and return the first QR code
            data_bytes = decoded_objects[0].data
            return data_bytes.decode("utf-8")

        return None
