# USAGE
# python ocr.py --image images/example_01.png
# python ocr.py --image images/example_02.png  --preprocess blur

# import the necessary packages
import numpy as np
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import pickle


with open('ppc.pickle', 'rb') as handle:
    ppc = pickle.load(handle)

for pg_num in range(1,40):
    print(pg_num)
    for part in range(0,ppc[pg_num]):
        filename = str(pg_num) +"Part "+ str(part) + '.bmp'

        # load the example image and convert it to grayscale
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cv2.imshow("Image", gray)

        # write the grayscale image to disk as a temporary file so we can
        # apply OCR to it
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)

        # load the image as a PIL/Pillow image, apply OCR, and then delete
        # the temporary file
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        print(text)
        print("\n\n\n\nNEXT PART")

