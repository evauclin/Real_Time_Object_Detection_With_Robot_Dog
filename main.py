#!python
import time
import numpy as np

last_detections = []

def main():
    dog.start()
    while cap.isOpened():
        if dog.is_ready():
            ret, frame = cap.read()
            image_np = np.array(frame)
            detections = detect_fn(image_np)
            current_class = classe_detector(detections)
            last_detections.append(current_class)
            if len(last_detections) > 5:
                last_detections.pop(0)

            current_order = check_if_all_classes_same(last_detections)
            if current_order is not None:
                dog.do(current_order)
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
