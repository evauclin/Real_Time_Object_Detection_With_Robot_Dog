#!/usr/bin/env python
import time

from pathlib import Path
import numpy as np
import os
from Tensorflow.models.research.object_detection.utils import config_util
from Tensorflow.models.research.object_detection.builders import model_builder
import tensorflow as tf
from tflite_runtime.interpreter import Interpreter

from typing import Any, List, Optional
from doggydo import doggy
from doggydo.doggy import DoggyOrder
from doggydo import detectorizer_without_tflite
from doggydo import detectorizer_for_tflite


def clamp_detections(detections: List[DoggyOrder], limit: int = 5) -> List[DoggyOrder]:
    """Clamp the number of detections to not exceed limit"""
    while len(detections) > limit:
        detections.pop(0)
    return detections


def get_order_given(last_detections: List[DoggyOrder]) -> DoggyOrder:
    """Returns the order to give as regard of all the detections given"""
    for order in DoggyOrder:
        if all(order == detection for detection in last_detections):
            return order
    return DoggyOrder.NONE


def get_new_detection_tflite(interpreter,frame,threshold):
    order = detectorizer_for_tflite.detect_objects(interpreter,frame,0.7)
    if order is not None:
        if order == '0':
            return DoggyOrder.LIE
        elif order == '1':
            return DoggyOrder.STAND
        elif order == '2':
            return DoggyOrder.SIT
        else:
            raise RuntimeError('Error with orders')
    return DoggyOrder.NONE


# def get_new_detection(frame: np.ndarray, model: Optional[Any]) -> DoggyOrder:
#     order = detectorizer_without_tflite.model_in_action(frame)
#     if order is not None:
#         if order == 'C':
#             return DoggyOrder.LIE
#         elif order == 'V':
#             return DoggyOrder.STAND
#         elif order == 'Y':
#             return DoggyOrder.SIT
#         else:
#             raise RuntimeError('Error with orders')
#     return DoggyOrder.NONE


def main():
    # Init vars and load models here
    last_detections = []
    # detection_model = detectorizer_without_tflite.setup_and_load_model()

    detection_model = Interpreter("detect_from_visio_dog.tflite")
    detection_model.allocate_tensors()

    # _, input_height, input_width, _ = detection_model.get_input_details()[0]['shape']

    if not doggy.start():
        raise RuntimeError("Doggy did not start!")

    new_detection = DoggyOrder.NONE

    # Main event loop
    while True:
        frame = doggy.get_camera_frame()
        if frame is not None:
            new_detection = get_new_detection_tflite(interpreter,frame,0.7)
            # new_detection = get_new_detection(frame, detection_model)
            last_detections.append(new_detection)
            last_detections = clamp_detections(last_detections, limit=5)
            current_order = get_order_given(last_detections)
            print(new_detection)

            if current_order != DoggyOrder.NONE and doggy.ready():
                doggy.do(current_order)
                last_detections = []
        else:
            print("I'll sleep to wait a little.")
            time.sleep(1)


if __name__ == "__main__":
    main()
