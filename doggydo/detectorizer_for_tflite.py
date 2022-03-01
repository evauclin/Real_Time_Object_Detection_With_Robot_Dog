from typing import Optional
import re
import time
from tflite_runtime.interpreter import Interpreter
import numpy as np

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def load_labels(path='labels.txt'):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels

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

    if not detections:
        return None

    unique_labels, counts = np.unique(detections, return_counts=True)
    max_count_idx = np.argmax(counts)
    max_label = unique_labels[max_count_idx]
    return max_label


if __name__ == "__main__":
    main()

