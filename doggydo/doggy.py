from distutils.log import warn
from enum import IntEnum

import cv2
import numpy as np
import time


class DoggyOrder(IntEnum):
    NONE = -1
    STAND = 1
    SIT = 2
    LIE = 3


class Doggy(object):
    def __init__(self):
        self._ready: bool = True
        self._cap = None

    def start(self) -> bool:
        self._cap = cv2.VideoCapture(0)
        return self._cap.isOpened()

    def ready(self):
        if self._cap is None or not self._cap.isOpened():
            return False
        return self._ready

    def do(self, action: DoggyOrder) -> bool:
        # TODO: this must be multithreaded.
        if not self.ready():
            return False
        print(f"Doggy will do: {action}")
        self._ready = False
        time.sleep(3)
        self._ready = True
        return True

    def get_camera_frame(self):
        if not self.ready():
            warn("May be we can retrieve image while doggy is acting?")
            return None

        ok, frame = self._cap.read()

        if not ok:
            raise RuntimeError(f"Could not read frame")

        return np.array(frame)
