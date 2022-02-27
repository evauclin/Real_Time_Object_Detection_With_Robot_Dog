#!/usr/bin/env python
import time

#from typing_extensions import Any, List, Optional
from doggydo import doggy
from doggydo.doggy import DoggyOrder


#def clamp_detections(detections: List[DoggyOrder], count: int = 5) -> List[DoggyOrder]:
def clamp_detections(detections, limit: int = 5):
    """Clamp the number of detections to not exceed limit"""
    while len(detections) > limit:
        detections = detections.pop(0)
    return detections


#def get_order_given(last_detections: List[DoggyOrder]) -> DoggyOrder:
def get_order_given(last_detections):
    """Returns the order to give as regard of all the detections given"""
    return DoggyOrder.NONE


#def get_new_detection(frame: np.ndarray) -> DoggyOrder:
def get_new_detection(frame):
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
