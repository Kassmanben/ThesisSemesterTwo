import io
import os

import PyPDF2
import time
import wand
import wand.image
from PIL.Image import new
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from wand.color import Color
from wand.image import Image

filename = "Algorithms.pdf"

inputpdf = PdfFileReader(open(filename, "rb"))

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    base = os.path.basename(filename)
    directory_name = os.path.splitext(base)[0]
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    new_filename = directory_name+"/page %s.pdf" % i
    if not os.path.exists(new_filename):
        with open(new_filename, "wb") as outputStream:
            output.write(outputStream)

    print(new_filename)
    try:
        img = Image(filename=new_filename,resolution=300)
    except:
        continue
    print('pages = ', len(img.sequence))

    converted =  img.convert('png')
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    new_filename = new_filename.replace(".pdf",".png")
    if not os.path.exists(new_filename):
        with open(new_filename, "wb") as outputStream:
            converted.save(filename=new_filename)
