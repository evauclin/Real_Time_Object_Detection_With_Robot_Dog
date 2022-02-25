import cv2
import uuid
import os
import time
import numpy as np

IMAGE_PATH = 'Tensorflow/workspace/images/collected_images'

if not os.path.isdir(IMAGE_PATH):
  os.mkdir(IMAGE_PATH)

labels = ['Y']
number_imgs = 15

cap = cv2. VideoCapture(0)
cv2.startWindowThread()

for label in labels:
    label_dir = os.path.join(IMAGE_PATH,label)
    if not os.path.isdir(label_dir):
      os.mkdir(label_dir)
  
    print(f"Collecting images for {label}")
    cv2.imshow('frame', np.zeros((100,100))) 
    print("Waiting for key to start...")
    k = cv2.waitKey(0)
    # press q key to close the program
    if k & 0xFF == ord('q'):
      break

    for imgnum in range(number_imgs):
        ret, frame = cap.read()
        imagename = os.path.join(label_dir, label+'.'+f'{str(uuid.uuid1())}.jpg')
        cv2.imwrite(imagename,frame)
        
        cv2.imshow('frame', frame)
        # time.sleep(2)
        print("Waiting for key to continue...")
        k = cv2.waitKey(0)
        
        # press q key to close the program
        if k & 0xFF == ord('q'):
          break

cap.release()
cv2.destroyAllWindows() 
