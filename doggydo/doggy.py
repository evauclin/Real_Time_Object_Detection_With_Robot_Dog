from enum import IntEnum

import time


class DoggyOrder(IntEnum):
    STAND = 1
    SIT = 2
    LIE = 3


class Doggy(object):
    def __init__(self):
        self._ready: bool = True

    def start(self) -> bool:
        return True

    def do(self, action: DoggyOrder) -> bool:
        time.sleep(2)
        return True

    def ready(self):
        return True
