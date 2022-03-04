from typing import Optional
import re
import time
from tflite_runtime.interpreter import Interpreter
import numpy as np


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = np.expand_dims((image-255)/255, axis=0)


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image, threshold) -> Optional[int]:
    """Returns a list of detection results, each a dictionary of object info."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    # Get all output details
    boxes = get_output_tensor(interpreter, 1)
    classes = get_output_tensor(interpreter, 3).astype(np.int)
    scores = get_output_tensor(interpreter, 0)
    count = int(get_output_tensor(interpreter, 2))

    detections = []
    for i in range(count):
        if scores[i] >= threshold:
           detections.append(classes[i])

    detections = np.array(detections)

    if detections.size == 0:
        return None

    unique_labels, counts = np.unique(detections, return_counts=True)
    max_count_idx = np.argmax(counts)
    max_label = unique_labels[max_count_idx]
    return max_label


if __name__ == "__main__":
    main()

