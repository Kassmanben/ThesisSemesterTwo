import numpy as np
import scipy.misc
import pickle
from PIL import Image
import pytesseract
import cv2
import os
import io
import PyPDF2
import wand
import wand.image
from wand.color import Color


def pdf_page_to_png(src_pdf, pagenum=0, resolution=72, ):
    """
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """
    dst_pdf = PyPDF2.PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(pagenum))

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = wand.image.Image(file=pdf_bytes, resolution=resolution)
    img.convert("png")
    img.background_color = Color("white")
    img.alpha_channel = "remove"

    return img


min_pg = 11
max_pg = 13

pdfFileObj = open('/Users/Ben/Downloads/Sedgewick_ALGORITHMS_ED4_3513.pdf', 'rb')
src_pdf = PyPDF2.PdfFileReader(pdfFileObj)

for pg_num in range(min_pg, max_pg):
    big_filename = str(pg_num) + ".png"
    pageObj = src_pdf.getPage(pg_num)
    img = pdf_page_to_png(src_pdf, pg_num, resolution=300)
    img.save(filename=big_filename)

width_of_whitespace = 23
isBorder = True
searching = False
pages_part_counters = {}


def mark_state(test_img):
    global isBorder, searching
    start_Coord = 0
    part_counter = 0
    border_whitespace_counter = 0
    for y in range(len(test_img)):
        # print(isBorder)
        if np.min(test_img[y]) == 255:
            isBorder = True
            border_whitespace_counter += 1

        else:
            isBorder = False
            border_whitespace_counter = 0

        if isBorder and searching and border_whitespace_counter > width_of_whitespace:
            scipy.misc.imsave(str(pg_num) + "Part " + str(part_counter) + '.bmp',
                              test_img[start_Coord:y])
            searching = False
            part_counter += 1

        if not isBorder and not searching:
            searching = True
            start_Coord = y
    pages_part_counters[pg_num] = part_counter


for x in range(min_pg, max_pg):
    # print(x)
    pg_num = x
    img = cv2.imread(str(pg_num) + '.png', 0)
    imageWidth = img.shape[1]  # Get image width
    imageHeight = img.shape[0]
    mark_state(img)

with open('ppc.pickle', 'wb') as handle:
    pickle.dump(pages_part_counters, handle, protocol=pickle.HIGHEST_PROTOCOL)

ocr_page_text = {}

for pg_num in range(min_pg, max_pg):
    print(pg_num)
    for part in range(0, pages_part_counters[pg_num]):
        filename = str(pg_num) + "Part " + str(part) + '.bmp'

        # load the image and convert it to grayscale
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
        text = text.replace("\n", " ")
        os.remove(filename)
        try:
            ocr_page_text[pg_num] += " " + text
        except KeyError:
            ocr_page_text[pg_num] = text

for page in ocr_page_text.keys():
    print(ocr_page_text[page])

with open('ocr_page_text.pickle', 'wb') as handle:
    pickle.dump(ocr_page_text, handle, protocol=pickle.HIGHEST_PROTOCOL)

pdfFileObj = open('/Users/Ben/Downloads/Sedgewick_ALGORITHMS_ED4_3513.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

correct_text_by_page = {}

for pg_num in range(min_pg, max_pg):
    pageObj = pdfReader.getPage(pg_num)
    page_text = pageObj.extractText()
    page_text = page_text.replace("\n", " ")
    correct_text_by_page[pg_num + 1] = page_text

for page in correct_text_by_page.keys():
    print(correct_text_by_page[page])

with open('correct_text_by_page.pickle', 'wb') as handle:
    pickle.dump(correct_text_by_page, handle, protocol=pickle.HIGHEST_PROTOCOL)
