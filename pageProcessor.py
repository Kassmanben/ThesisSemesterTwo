import shutil

import numpy as np
import re
import scipy.misc
import pickle
from PIL import Image
import pytesseract
import cv2
import os
import io
import PyPDF2
import difflib

import wand
import wand.image
from wand.color import Color

filename = 'Sedgewick_ALGORITHMS_ED4_3513.pdf'
base = os.path.basename(filename)
directory_name = os.path.splitext(base)[0]

pdfFileObj = open(filename, 'rb')
src_pdf = PyPDF2.PdfFileReader(pdfFileObj)

width_of_whitespace = 23
isBorder = True
searching = False
pages_part_counters = {}
ocr_page_text = {}

pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

correct_text_by_page = {}

final_text = {}


def mark_state(test_img, page_num):
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
            if not os.path.exists(directory_name + " Parts"):
                os.makedirs(directory_name + " Parts")
            scipy.misc.imsave(directory_name + " Parts/Page " + str(pg_num) + "part %s.bmp" % part_counter,
                              test_img[start_Coord:y])
            searching = False
            part_counter += 1

        if not isBorder and not searching:
            searching = True
            start_Coord = y
    pages_part_counters[page_num] = part_counter


def process_page(page_num):
    pageObj = pdfReader.getPage(page_num - 1)
    page_text = pageObj.extractText()
    page_text = page_text.replace("\n", " ")
    correct_text_by_page[page_num] = page_text

    if page_num < 10:
        temp_img = cv2.imread("Algorithms/Algorithms-0" + str(page_num) + '.png', 0)
    else:
        temp_img = cv2.imread("Algorithms/Algorithms-" + str(page_num) + '.png', 0)

    mark_state(temp_img, page_num)

    if pages_part_counters[page_num] == 0:
        ocr_page_text[page_num] = "Blank page"

    for part in range(0, pages_part_counters[page_num]):
        bmp_filename = directory_name + " Parts/Page " + str(pg_num) + "part %s.bmp" % part

        text = pytesseract.image_to_string(Image.open(bmp_filename))
        text = text.replace("\n", " ")

        try:
            ocr_page_text[page_num] += " " + text
        except KeyError:
            ocr_page_text[page_num] = text


def fill_final_text(page_number, ocr_text, pdf_text):
    str = ""
    error = {"ocr": [], "pdf": []}

    ocr_text = ocr_text.split(".")
    pdf_text = pdf_text.split(".")

    diff = difflib.unified_diff(ocr_text, pdf_text)
    for e in list(diff):
        if(e.startswith("+")):
            print(e)


min_pg = 12
max_pg = 14

pg_num = 12

# for pg_num in range(min_pg, max_pg):
#     print(pg_num)
process_page(pg_num)

# for pg_num in range(min_pg, max_pg):
ocr_page_text[pg_num] = clean_up_string(ocr_page_text[pg_num])
correct_text_by_page[pg_num] = clean_up_string(correct_text_by_page[pg_num])
fill_final_text(pg_num, ocr_page_text[pg_num], correct_text_by_page[pg_num])

shutil.rmtree(directory_name + " Parts")
