#!/usr/bin/env python
import time

#from typing_extensions import Any, List, Optional
from doggydo import doggy
from doggydo.doggy import DoggyOrder


#def clamp_detections(detections: List[Any], count: int = 5) -> List[Any]:
def clamp_detections(detections, count: int = 5):
    while len(detections) > count:
        detections = detections.pop(0)
    return detections


#def get_order_given(last_detections: List[Any]) -> Optional[DoggyOrder]:
def get_order_given(last_detections):
    return None


#def get_new_detection() -> Any:
def get_new_detection():
    return None


def main():
    last_detections = []

    if not doggy.start():
        raise RuntimeError("Doggy did not start!")

    while True:
        if doggy.ready():
            new_detection = get_new_detection()
            if new_detection is not None:
                last_detections.append(new_detection)
            last_detections = clamp_detections(last_detections)
            current_order = get_order_given(last_detections)

            if current_order is not None:
                doggy.do(current_order)
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
