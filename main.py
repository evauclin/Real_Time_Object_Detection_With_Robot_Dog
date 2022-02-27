#!/usr/bin/env python
import time

import numpy as np

from typing import List
from doggydo import doggy
from doggydo.doggy import DoggyOrder


def clamp_detections(detections: List[DoggyOrder], limit: int = 5) -> List[DoggyOrder]:
    """Clamp the number of detections to not exceed limit"""
    while len(detections) > limit:
        detections.pop(0)
    return detections


def get_order_given(last_detections: List[DoggyOrder]) -> DoggyOrder:
    """Returns the order to give as regard of all the detections given"""
    return DoggyOrder.NONE


def get_new_detection(frame: np.ndarray) -> DoggyOrder:
    """Run the prediction and return the Detection observed"""
    return DoggyOrder.NONE


def main():
    last_detections = []

    if not doggy.start():
        raise RuntimeError("Doggy did not start!")

    while True:
        frame = doggy.get_camera_frame()
        if frame is not None:
            new_detection = get_new_detection(frame)
            last_detections.append(new_detection)
            last_detections = clamp_detections(last_detections)
            current_order = get_order_given(last_detections)

            if current_order != DoggyOrder.NONE and doggy.ready():
                doggy.do(current_order)
                last_detections = []
        else:
            print("I'll sleep to wait a little.")
            time.sleep(1)


if __name__ == "__main__":
    main()
