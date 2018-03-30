import shutil

import numpy as np
import re
import scipy.misc
import unicodedata
from PIL import Image
import pytesseract
import cv2
import os
import PyPDF2
from difflib import SequenceMatcher

en_dict_file = open("Dictionary.txt", "r")
en_dict = set([x.strip() for x in en_dict_file.readlines()])

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


def _edit_dist_init(len1, len2):
    lev = []
    for i in range(len1):
        lev.append([0] * len2)  # initialize 2D array to zero
    for i in range(len1):
        lev[i][0] = i  # column 0: 0,1,2,3,4,...
    for j in range(len2):
        lev[0][j] = j  # row 0: 0,1,2,3,4,...
    return lev


def _edit_dist_step(lev, i, j, s1, s2, substitution_cost=1, transpositions=False):
    c1 = s1[i - 1]
    c2 = s2[j - 1]

    # skipping a character in s1
    a = lev[i - 1][j] + 1
    # skipping a character in s2
    b = lev[i][j - 1] + 1
    # substitution
    c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

    # transposition
    d = c + 1  # never picked by default
    if transpositions and i > 1 and j > 1:
        if s1[i - 2] == c2 and s2[j - 2] == c1:
            d = lev[i - 2][j - 2] + 1

    # pick the cheapest
    lev[i][j] = min(a, b, c, d)


def edit_distance(s1, s2, substitution_cost=1, transpositions=False):
    s1 = clean_up(s1)
    s2 = clean_up(s2)

    # set up a 2-D array
    len1 = len(s1)
    len2 = len(s2)
    lev = _edit_dist_init(len1 + 1, len2 + 1)

    # iterate over the array
    for i in range(len1):
        for j in range(len2):
            _edit_dist_step(lev, i + 1, j + 1, s1, s2,
                            substitution_cost=substitution_cost, transpositions=transpositions)
    return lev[len1][len2] < .8 * (min(len1, len2))


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
            scipy.misc.imsave(directory_name + " Parts/Page " + str(page_num) + "part %s.bmp" % part_counter,
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
        bmp_filename = directory_name + " Parts/Page " + str(page_num) + "part %s.bmp" % part

        text = pytesseract.image_to_string(Image.open(bmp_filename))
        text = text.replace("\n", " ")

        try:
            ocr_page_text[page_num] += " " + text
        except KeyError:
            ocr_page_text[page_num] = text


def deal_with_odd_characters(str_to_deal_with):
    for char_and_replacement in [("Ꜳ", "AA"), ("ꜳ", "aa"), ("Æ", "AE"), ("æ", "ae"), ("Ꜵ", "AO"), ("ꜵ", "ao"),
                                 ("Ꜷ", "AU"), ("ꜷ", "au"), ("Ꜹ", "AV"), ("ꜹ", "av"), ("Ꜻ", "AV"), ("ꜻ", "av"),
                                 ("Ꜽ", "AY"), ("ꜽ", "ay"), ("ﬀ", "ff"), ("ﬃ", "ffi"), ("ﬄ", "ffl"), ("ﬁ", "fi"),
                                 ("ﬂ", "fl"), ("Œ", "OE"), ("œ", "oe"), ("Ꝏ", "OO"), ("ꝏ", "oo"), ("ẞ", "ſs"),
                                 ("ß", "ſz"),
                                 ("ﬆ", "st"), ("ﬅ", "ſt"), ("Ꜩ", "TZ"), ("ꜩ", "tz"), ("ᵫ", "ue"), ("Ꝡ", "VY"),
                                 ("ꝡ", "vy")]:
        pc = char_and_replacement[0]
        rc = char_and_replacement[1]
        if str_to_deal_with.__contains__(pc):
            temp = str_to_deal_with.split()
            str_to_deal_with = ""
            for i in range(0, len(temp)):
                new_word = temp[i]
                fixed = False
                if temp[i].__contains__(pc):
                    try:
                        if new_word.__contains__(pc):
                            if temp[i - 1] + temp[i].replace(pc, rc) + temp[i + 1] in en_dict and not fixed:
                                new_word = temp[i].replace(pc, rc) + temp[i + 1]
                                str_to_deal_with = str_to_deal_with[:-1]
                                temp[i + 1] = ""
                                fixed = True
                    except IndexError:
                        pass
                    try:
                        if temp[i - 1] + temp[i].replace(pc, rc) in en_dict and not fixed:
                            new_word = temp[i].replace(pc, rc)
                            str_to_deal_with = str_to_deal_with[:- 1]
                            fixed = True
                    except IndexError:
                        pass
                    try:
                        if temp[i].replace(pc, rc) + temp[i + 1] in en_dict and not fixed:
                            new_word = temp[i].replace(pc, rc) + temp[i + 1]
                            temp[i + 1] = ""
                            fixed = True
                    except IndexError:
                        pass
                if not fixed and new_word.replace(pc, rc) in en_dict:
                    new_word = new_word.replace(pc, rc)

                str_to_deal_with += new_word + " "
    return str_to_deal_with


def clean_up(str_to_clean):
    str_to_clean = deal_with_odd_characters(str_to_clean)
    str_to_clean = unicodedata.normalize('NFKD', str_to_clean).encode('ascii', 'ignore').decode("utf-8")
    str_to_clean = re.sub('\s+', " ", str_to_clean)
    while re.search('\.\s+\.', str_to_clean):
        str_to_clean = re.sub('\.\s+\.', "..", str_to_clean)
    while re.search('_{2,}', str_to_clean):
        str_to_clean = re.sub('_{2,}', "", str_to_clean)
    if re.search('^([clxvi]{1,8}[A-Z])|^([CLXVI]{1,8}[A-Z])', str_to_clean):
        if str_to_clean.split()[0].lower() not in en_dict:
            m = re.match('^([clxvi]{1,8}[A-Z])|^([CLXVI]{1,8}[A-Z])', str_to_clean)
            str_to_clean = str_to_clean[:m.end(0) - 1] + " " + str_to_clean[m.end(0) - 1:]
    split = str_to_clean.split()
    str_to_clean = ""
    for w in split:
        new_word = w
        if re.search('^[0-9]+[a-zA-Z]', w) and w not in en_dict:
            m = re.match('^[0-9]+[a-zA-Z]', w)
            new_word = str(w[:m.end(0) - 1]) + " " + str(w[m.end(0) - 1:])
        str_to_clean += (str(new_word) + " ")

    return str_to_clean

# Look into dna processing. Look for long, common substrings.
# Keep doing that, use a boolean set of regions to keep track of what is accounted for
# Use a distance metric to determine closeness of remaining regions


def fill_final_text(page_num, ocr_text, pdf_text):
    print("Page: ", page_num)
    percentage = SequenceMatcher(None, ocr_text, pdf_text).ratio()
    if percentage > .95:
        final_text[page_num] = pdf_text
    else:
        osplit = ocr_text.split()
        psplit = pdf_text.split()
        max_length = max(len(osplit), len(psplit))

        temp = ["" for x in range(max_length)]
        if not osplit:
            temp = psplit
        if not psplit:
            temp = osplit

        for i in range(0, max_length):
            try:
                if edit_distance(osplit[i], psplit[i]):
                    temp[i] = psplit[i]
                    osplit[i] = ""
                    psplit[i] = ""
            except IndexError:
                continue

        for o in range(0, len(osplit)):
            if osplit[o] != "":
                for p in range(0, len(psplit)):
                    if psplit[p] == "":
                        continue
                    if re.match('^[.?!\-_—)(}{\]\[;:\'\"]+$', psplit[p]):
                        try:
                            psplit[p + 1] = psplit[p] + psplit[p + 1]
                            psplit[p] = ""
                        except IndexError:
                            psplit[p - 1] = psplit[p - 1] + psplit[p]
                            psplit[p] = ""
                    if edit_distance(osplit[o], psplit[p]):
                        temp[o] = psplit[p]
                        osplit[o] = ""
                        psplit[p] = ""
                        break
                    if psplit[p].startswith(osplit[o]):
                        try:
                            if edit_distance(psplit[p][:len(osplit[o])], osplit[o]) and edit_distance(
                                    psplit[p][len(osplit[o]):], osplit[o + 1]):
                                temp[o] = psplit[p][:len(osplit[o])]
                                temp[o + 1] = psplit[p][len(osplit[o]):]
                                osplit[o] = ""
                                osplit[o + 1] = ""
                                psplit[p] = ""
                                break
                        except IndexError:
                            pass
                    if osplit[o].endswith(psplit[p]):
                        try:
                            if edit_distance(osplit[o], psplit[p - 1] + " " + psplit[p]):
                                temp[o] = psplit[p - 1] + " " + psplit[p]
                                osplit[o] = ""
                                psplit[p - 1] = ""
                                psplit[p] = ""
                        except IndexError:
                            pass

        osplit = [x for x in osplit if x != '']
        psplit = [x for x in psplit if x != '']

        print("temp:", temp)
        print("Osplit: ", osplit)
        print("Psplit: ", psplit)
        print()


min_pg = 6
max_pg = 15

for pg_num in range(min_pg, max_pg):
    process_page(pg_num)
    ocr_page_text[pg_num] = clean_up(ocr_page_text[pg_num])
    correct_text_by_page[pg_num] = clean_up(correct_text_by_page[pg_num])
    fill_final_text(pg_num, ocr_page_text[pg_num], correct_text_by_page[pg_num])

for key, value in final_text.items():
    print(final_text[key])

shutil.rmtree(directory_name + " Parts")
