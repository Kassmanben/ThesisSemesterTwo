import logging
import pickle
import re
import unicodedata
import os
import xml
from subprocess import check_output
import xml.etree.ElementTree as ET
from PyPDF2 import PdfFileReader

from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1

en_dict_file = open("Dictionary.txt", "r")
en_dict = set([x.strip() for x in en_dict_file.readlines()])

filename = 'Sedgewick_ALGORITHMS_ED4_3513.pdf'
base = os.path.basename(filename)
directory_name = os.path.splitext(base)[0]

width_of_whitespace = 23
isBorder = True
searching = False
pages_part_counters = {}
ocr_page_text = {}

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


def deal_with_odd_characters(str_to_deal_with):
    str_to_deal_with = str_to_deal_with.replace("(cid:81)(cid:3)", "■")
    str_to_deal_with = str_to_deal_with.replace("(cid:81)", "■")
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
    if str_to_clean.__contains__("-"):
        s = str_to_clean.split()
        str_to_clean = ""
        for i in range(0, len(s)):
            try:
                if s[i].__contains__("-") and s[i].replace("-", "") + s[i + 1] in en_dict:
                    str_to_clean += " " + s[i].replace("-", "") + s[i + 1]
                    s[i + 1] = ""
                else:
                    str_to_clean += " " + s[i]
            except IndexError:
                str_to_clean += " " + s[i]
    split = str_to_clean.split()
    str_to_clean = ""
    for i in range(0, len(split)):
        try:
            if split[i] not in en_dict and split[i] + split[i + 1] in en_dict:
                str_to_clean += " " + split[i].replace("-", "") + split[i + 1]
                split[i + 1] = ""
            else:
                str_to_clean += " " + split[i]
        except IndexError:
            str_to_clean += " " + split[i]

    return str_to_clean


def process_page(page_num):
    pg_text = check_output(
        ["pdf2txt.py -p " + str(page_num) + " /Users/rosie/Ben_Stuff/Sedgewick_ALGORITHMS_ED4_3513.pdf"],
        shell=True).decode("utf-8")
    text_sections = pg_text.split("\n\n")
    text_sections_c = text_sections.copy()
    text_sections = []
    for t in text_sections_c:
        temp = clean_up(t)
        if temp.__contains__("■"):
            text_sections.append(temp.split("■")[0])
            for i in temp.split("■")[1:]:
                text_sections.append("■" + i)
        else:
            text_sections.append(temp)

    return text_sections


def get_tag_elem(e, tag):
    for a in e:
        if a.tag == tag:
            return str(a.text)


def tag_toc_elements(e):
    global tag_dict
    root = e.getroot()
    for child in root:
        try:
            tag_dict[str(int(get_tag_elem(child, "pageno")) + 1)].append(
                ("level" + child.attrib["level"], child.attrib["title"][2:-1]))
        except KeyError:
            tag_dict[str(int(get_tag_elem(child, "pageno")) + 1)] = [
                ("level" + child.attrib["level"], child.attrib["title"][2:-1])]


def get_toc():
    pg_text = check_output(
        ["dumppdf.py -T /Users/rosie/Ben_Stuff/Sedgewick_ALGORITHMS_ED4_3513.pdf"],
        shell=True).decode("utf-8")
    return ET.ElementTree(ET.fromstring(pg_text))


toc = get_toc()
tag_dict = {}
tag_toc_elements(toc)
pdf = PdfFileReader(open('/Users/rosie/Ben_Stuff/Sedgewick_ALGORITHMS_ED4_3513.pdf', 'rb'))
min_pg = 0
max_pg = pdf.getNumPages()

logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)

with open('tag_dict.pickle', 'wb') as handle:
    pickle.dump(tag_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('pages.pickle', 'wb') as handle:
    pickle.dump([], handle, protocol=pickle.HIGHEST_PROTOCOL)

for pg_num in range(min_pg, max_pg):
    print(str(pg_num) + " out of " + str(max_pg))

    with open('pages.pickle', 'rb') as handle:
        pages = pickle.load(handle)

    pages.append(process_page(pg_num))

    with open('pages.pickle', 'wb') as handle:
        pickle.dump(pages, handle, protocol=pickle.HIGHEST_PROTOCOL)


