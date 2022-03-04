import io
from distutils.log import warn
from enum import IntEnum
import subprocess
from PIL import Image

import numpy as np
import time
from typing import List

from .controller.Action import Action
from .controller.Led import Led
from .controller.Buzzer import Buzzer


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
            img = Image.open(io.BytesIO(jpg)).resize((320, 320))
            frame = np.array(img).astype(np.float32)
            return True, frame
        return False, None


DOGGY_IDLE_POSITION = [[55,78,0],[55,78,0],[55,78,0],[55,78,0]]
DOGGY_SIT_POSITION = [[-20,120,-20],[50,105,0],[50,105,0],[-20,120,20]]
DOGGY_STAND_POSITION = [[0, 99, 10], [0, 99, 10], [0, 99, -10], [0, 99, -10]]


class DoggyAnimator(object):
    def __init__(self):
        self.controller = Action()
        time.sleep(2)

    @property
    def position(self):
        return self.controller.control.point

    def interpolate_to(self, xyz: List[List[float]], steps: int, pause: float):
        for i in range(4):
            xyz[i][0]=(xyz[i][0]-self.controller.control.point[i][0])/steps
            xyz[i][1]=(xyz[i][1]-self.controller.control.point[i][1])/steps
            xyz[i][2]=(xyz[i][2]-self.controller.control.point[i][2])/steps
        for j in range(steps):
            for i in range(4):
                self.controller.control.point[i][0]+=xyz[i][0]
                self.controller.control.point[i][1]+=xyz[i][1]
                self.controller.control.point[i][2]+=xyz[i][2]
            self.controller.control.run()
            time.sleep(pause)


class Doggy(object):
    def __init__(self):
        self._ready: bool = True
        self.video = None
        self._machine = None
        self.in_stand = False
        self.last_order = DoggyOrder.LIE

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
        self.animator = DoggyAnimator()
        # self.led = Led()
        self.buzzer = Buzzer()
        return self.video.is_opened()

    def ready(self):
        if self.video is None or not self.video.is_opened():
            return False
        return self._ready

    def do(self, order: DoggyOrder) -> bool:
        # TODO: this must be multithreaded?
        if not self.ready():
            return False

        self._ready = False

        # if order != DoggyOrder.NONE and order != self.last_order and self.in_stand:
        #     self.animator.controller.lay2(enter=False)
        #     self.in_stand = False

        if not self.is_raspberrypi:
            print("NO DOGGY ON PC")
            time.sleep(3)
        elif self.last_order != order:
            if order == DoggyOrder.STAND:
                print("STAND")
                # self.animator.controller.lay2(enter=True)
                # self.in_stand = True
                self.buzzer.run('1')
                time.sleep(0.2)
                self.buzzer.run('0')
                time.sleep(0.1)
                self.buzzer.run('1')
                time.sleep(0.2)
                self.buzzer.run('0')
                time.sleep(0.4)
                self.buzzer.run('1')
                time.sleep(0.3)
                self.buzzer.run('0')
            elif order == DoggyOrder.SIT:
                print("SIT")
                self.animator.interpolate_to(xyz=DOGGY_SIT_POSITION, steps=30, pause=0.02)
                self.last_order = order
            elif order == DoggyOrder.LIE:
                print("LIE")
                self.animator.interpolate_to(xyz=DOGGY_IDLE_POSITION, steps=30, pause=0.02)
                self.last_order = order
            elif order == DoggyOrder.NONE:
                print("NONE")
                self.last_order = order
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
