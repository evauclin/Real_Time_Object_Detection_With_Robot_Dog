import io
from distutils.log import warn
from enum import IntEnum
import subprocess
from PIL import Image

import numpy as np
import time

from .controller.Action import Action


class DoggyOrder(IntEnum):
    NONE = -1
    STAND = 1
    SIT = 2
    LIE = 3


class CV2Camera(object):
    def __init__(self):
        import cv2
        self._cap = cv2.VideoCapture(0)

    def setup(self):
        pass

    def is_opened(self):
        return self._cap.isOpened()

    def get_frame(self, stream: io.BytesIO = None):
        if self.is_opened():
            ret, frame = self._cap.read()
            return ret, np.array(frame) if ret else frame


class PiCamera(object):
    def __init__(self):
        import picamera
        self.camera = picamera.PiCamera()

    def setup(self):
        self.camera.resolution = (400,300)       # pi camera resolution
        self.camera.framerate = 15               # 15 frames/sec
        self.camera.saturation = 80              # Set image video saturation
        self.camera.brightness = 50              # Set the brightness of the image (50 indicates the state of white balance)

    def is_opened(self):
        return True

    def is_valid_image_4_bytes(self,buf):
        bValid = True
        if buf[6:10] in (b'JFIF', b'Exif'):
            if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
                bValid = False
        else:
            try:
                Image.open(io.BytesIO(buf)).verify()
            except:
                bValid = False
        return bValid

    def get_frame(self, stream: io.BytesIO):
        stream.seek(0)
        jpg = stream.read()
        stream.seek(0)
        stream.truncate()
        if self.is_valid_image_4_bytes(jpg):
            img = Image.open(io.BytesIO(jpg))
            return True, np.array(img)
        return False, None


class Doggy(object):
    def __init__(self):
        self._ready: bool = True
        self.video = None
        self._machine = None

    @property
    def machine(self):
        if not self._machine:
            self._machine = subprocess.getoutput('uname -n')
        return self._machine

    @property
    def is_raspberrypi(self):
        return self.machine == "raspberrypi"

    def start(self) -> bool:
        print("Starting...")
        self.video = CV2Camera() if not self.is_raspberrypi else PiCamera()
        self.controller = Action()
        time.sleep(2)
        return self.video.is_opened()

    def ready(self):
        if self.video is None or not self.video.is_opened():
            return False
        return self._ready

    def do(self, order: DoggyOrder) -> bool:
        # TODO: this must be multithreaded?
        if not self.ready():
            return False

        print(f"Doggy will do: {order}")
        self._ready = False

        if not self.is_raspberrypi:
            time.sleep(3)
        elif order == DoggyOrder.STAND:
            print("STAND")
        elif order == DoggyOrder.SIT:
            print("SIT")
        elif order == DoggyOrder.LIE:
            self.controller.lay_in()
            time.sleep(2)
            self.controller.lay_out()
        elif order == DoggyOrder.NONE:
            print("NONE")
        else:
            raise RuntimeError(f"Unknown order: {order}")

        self._ready = True
        return True

    def get_camera_frame(self, stream: io.BytesIO = None) -> np.ndarray:
        if not self.ready():
            warn("May be we can retrieve image while doggy is acting?")
            return None

        ok, frame = self.video.get_frame(stream)

        if not ok:
            raise RuntimeError(f"Could not read frame")

        return frame
