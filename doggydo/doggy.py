from distutils.log import warn
from enum import IntEnum

import time


class DoggyOrder(IntEnum):
    NONE = -1
    STAND = 1
    SIT = 2
    LIE = 3


class Doggy(object):
    def __init__(self):
        self._ready: bool = True

    def start(self) -> bool:
        return True

    def do(self, action: DoggyOrder) -> bool:
        # TODO: this must be multithreaded.
        if not self.ready():
            return False
        self._ready = False
        time.sleep(2)
        self._ready = True
        return True

    def ready(self):
        return True

    def get_camera_frame(self):
        if not self.ready():
            warn("May be we can retrieve image while doggy is acting?")
            return None
        return None
