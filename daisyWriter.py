import pickle
from xml.dom import minidom
from xml.etree.cElementTree import *
import lxml.etree as etree
from PyPDF2 import PdfFileReader

dc_metadata = {"Title": "REQUIRED", "Creator": "Unknown", "Subject": "Unknown", "Description": "Unknown",
               "Publisher": "REQUIRED", "Contributor": "Unknown", "Date": "REQUIRED", "Type": "Unknown",
               "Format": "REQUIRED", "Identifier": "REQUIRED", "Source": "Unknown", "Language": "REQUIRED",
               "Relation": "Unknown", "Coverage": "Unknown", "Rights": "Unknown"}
dtb_metadata = {"sourceDate": "Unknown", "sourceEdition": "Unknown", "sourcePublisher": "Unknown",
                "sourceTitle": "Unknown", "multimediaType": "REQUIRED", "multimediaContent": "REQUIRED",
                "narrator": "Unknown", "producer": "Unknown", "producedDate": "Unknown", "revision": "Unknown",
                "revisionDate": "Unknown", "revisionDescription": "Unknown", "totalTime": "REQUIRED",
                "audioFormat": "Unknown", "uid": "REQUIRED"}
nav_metadata = {"uid": "REQUIRED", "depth": "REQUIRED", "generator": "Unknown", "totalPageCount": "REQUIRED",
                "maxPageNumber": "REQUIRED"}
ncx_smil_metadata = {"id": "REQUIRED", "defaultState": 'false', "override": 'hidden', "bookStruct": "PAGENUMBER"}

smil_metadata = {"uid": "REQUIRED", "generator": "Unknown", "totalElapsedTime": "REQUIRED"}

element_count = {}


# Returns the number of this elementtag already present in the file.
# By default, returns as a string "_ddddd" where ddddd is the count, preceded by 0s
def get_element_count(elem_name, update=False, return_format=str):
    global element_count
    try:
        e = element_count[elem_name]
    except KeyError:
        element_count[elem_name] = 0
    if return_format is not str:
        if update:
            element_count[elem_name] += 1
            return element_count[elem_name] - 1
        else:
            return element_count[elem_name]
    else:
        if update:
            element_count[elem_name] += 1
            return "_" + ("0" * (5 - len(str(element_count[elem_name] - 1))) + str(element_count[elem_name] - 1))
        else:
            return "_" + ("0" * (5 - len(str(element_count[elem_name]))) + str(element_count[elem_name]))


# QuickElementCount Get element count id quickly, returns tag as usually desired: "TAG_ddddd"
def qec(elem_name):
    return elem_name + get_element_count(elem_name, update=True)


def make_meta_tags(head_elem, l, mode=None):
    if not mode:
        return
    meta_dict = {}
    meta_dict2 = {}
    prefix_e = "dtb:"
    prefix_e2 = ""
    if mode is "ncx":
        meta_dict = nav_metadata
    elif mode is "smil":
        meta_dict = smil_metadata
    elif mode is 'xml':
        meta_dict = dtb_metadata
        meta_dict2 = dc_metadata
        prefix_e2 = "dc:"
    for e in l.keys():
        if l[e] is not None and e in meta_dict.keys():
            prefix_e += e
            meta_elem = SubElement(head_elem, "meta", name=prefix_e, content=str(l[e]))
        if mode == "xml" and l[e] is not None and e in meta_dict2.keys():
            prefix_e2 += e
            if e != "Creator":
                meta_elem2 = SubElement(head_elem, "meta", name=prefix_e2, content=str(l[e]))
            else:
                meta_elem2 = SubElement(head_elem, "meta", name=prefix_e2, content=", ".join(l[e]))


def required_attribs(dc=False, dtb=False, ncx_smil=False, nav=False, smil=False):
    global dc_metadata, dtb_metadata, ncx_smil_metadata
    required_args = set()
    if dc:
        for e in dc_metadata.keys():
            if dc_metadata[e] == "REQUIRED":
                required_args.add(e)
    if dtb:
        for e in dtb_metadata.keys():
            if dtb_metadata[e] == "REQUIRED":
                required_args.add(e)
    if nav:
        for e in nav_metadata.keys():
            if nav_metadata[e] == "REQUIRED":
                required_args.add(e)
    if smil:
        for e in smil_metadata.keys():
            if smil_metadata[e] == "REQUIRED":
                required_args.add(e)
    if ncx_smil:
        for e in ncx_smil_metadata.keys():
            if ncx_smil_metadata[e] == "REQUIRED":
                required_args.add(e)
    return required_args


def start_ncx_file(attribs=None):
    ncx = Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1", attrib={"xml:lang": "eng"})
    head = SubElement(ncx, "head")

    smil_custom_test = SubElement(head, "smilCustomTest")
    for s in ncx_smil_metadata.keys():
        try:
            smil_custom_test.set(s, attribs[s])
        except KeyError:
            smil_custom_test.set(s, ncx_smil_metadata[s])

    make_meta_tags(head, attribs, mode="ncx")

    doc_title = SubElement(ncx, "docTitle")
    doc_title_text = SubElement(doc_title, "text")
    doc_title_text.text = attribs["Title"]

    if "Creator" in attribs.keys():
        doc_author = SubElement(ncx, "docAuthor")
        doc_author_text = SubElement(doc_author, "text")
        if type(attribs["Creator"]) is list:
            authors = attribs["Creator"][0]
            if len(attribs["Creator"]) > 2:
                authors += ","
                for i in range(1, len(attribs["Creator"]) - 1):
                    authors += " " + attribs["Creator"][i] + ","
            authors += " and " + attribs["Creator"][-1]
            doc_author_text.text = authors
        else:
            doc_author_text.text = str(attribs["Creator"])

    nav_map = SubElement(ncx, "navMap")

    return ncx


def start_smil_files(attribs=None):
    smil_filename = attribs["Title"] + ".smil"
    smil = Element("smil", xmlns="http://www.w3.org/2001/SMIL20/")

    head = SubElement(smil, "head")

    make_meta_tags(head, attribs, mode="smil")

    layout = SubElement(head, "layout")
    layout_region = SubElement(layout, "region", id="textRegion", height="auto", width="auto", bottom="auto",
                               top="auto", left="auto", right="auto", fit="hidden", showBackground="always")

    custom_attributes = SubElement(head, "customAttributes")
    custom_test = SubElement(custom_attributes, "customTest", id="pagenumCustomTest", defaultState="false",
                             override="visible")

    body = SubElement(smil, "body")
    seq = SubElement(body, "seq", id="baseseq", attrib={"class": "book"}, fill="remove")

    return smil


def start_xml_file(attribs=None):
    dtbook = Element("dtbook", xmlns="http://www.w3.org/2001/SMIL20/")

    head = SubElement(dtbook, "head")

    make_meta_tags(head, attribs, mode="xml")

    book = SubElement(dtbook, "book", id=attribs["Identifier"])
    front_matter = SubElement(book, "frontmatter", id=qec("frontmatter"))
    doc_title = SubElement(front_matter, "doctitle", id=qec("doctitle"))
    doc_title.text = attribs["Title"]
    if "Creator" in attribs.keys():
        if type(attribs["Creator"]) is list:
            for c in attribs["Creator"]:
                doc_author = SubElement(front_matter, "docauthor", id=qec("docauthor"))
                doc_author.text = c
        else:
            doc_author = SubElement(front_matter, "docauthor", id=qec("docauthor"))
            doc_author.text = attribs["Creator"]
    body_matter = SubElement(book, "bodymatter", id=qec("bodymatter"))

    return dtbook


def write_file(title, file_type, starting_lines, element_tree):
    filename = title + file_type
    tree = ElementTree(element_tree)
    tree.write(filename)
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    f = open(filename, "w")
    for s in starting_lines:
        f.write(s)
    for l in lines:
        l.replace('<?xml version="1.0" ?>', "")
        f.write(l)

    # xmlstr = minidom.parseString(tostring(element_tree)).toprettyxml(indent="     ")


def fill_in_page_text(ncx, smil, xml, num, level_info, attribs, multiple_tags=False):
    l_list = level_info[1]
    l_index = level_info[2]
    page_num = SubElement(l_list[l_index], "pagenum", page="normal", id="p" + str(num),
                          smilref=str(qec(attribs["Title"])) + ".smil#p" + str(num))


def fill_in_tags(ncx, smil, xml, attribs):
    global tag_dict, pages, max_pg

    level1 = 0
    level1_list = []

    level2 = -1
    level2_counter = 0
    level2_list = []

    level3 = -1
    level3_counter = 0
    level3_list = []

    current_level = ""
    page = 1
    multiple_tags=False
    for i in range(0, max_pg):
        if str(i) in tag_dict.keys():
            for e in tag_dict[str(i)]:
                if(len(tag_dict[str(i)])>1):
                    multiple_tags=True
                try:
                    if e[1] == "Contents":
                        toc = SubElement(xml.find(".//frontmatter"), "level1", id="toc")
                        level1_list.append(toc)
                        fill_in_page_text(ncx, smil, xml, i, ["level1", level1_list, level1], attribs)

                    if e[1] == "Preface":
                        level1 += 1
                        pref = SubElement(xml.find(".//frontmatter"), "level1", id="pref")
                        level1_list.append(pref)
                        fill_in_page_text(ncx, smil, xml, i, ["level1", level1_list, level1], attribs)

                    if e[0] == "level1" and e[1] != "Contents" and e[1] != "Preface":
                        sub_element = SubElement(xml.find(".//bodymatter"), "level1", id="ch" + str(level1))
                        section = SubElement(sub_element, "section", attrib={"epub:type": "chapter"}, id=qec("section"))
                        header = SubElement(section, "header", id=qec("header"))
                        pagenum = SubElement(header, "pagenum", attrib={"epub:type": "pagebreak"}, id="p" + str(i),
                                             page="normal", smilref=str(qec(attribs["Title"])) + ".smil#p" + str(i))
                        h1 = SubElement(header, "h1", id="ch" + str(level1) + "-start",
                                        attrib={"xml:space": "preserve"},
                                        smilref=str(qec(attribs["Title"])) + ".smil#ch" + str(level1) + "-start")
                        h1.text = e[1]
                        level1 += 1
                        level2_counter = 0
                        level3_counter = 0
                        level1_list.append(sub_element)
                        current_level = "level1"
                        fill_in_page_text(ncx, smil, xml, i, ["level1", level1_list, level1], attribs)


                    if e[0] == "level2":
                        level2 += 1
                        level2_counter += 1
                        sub_element = SubElement(level1_list[level1 + 1], "level2", id=qec("level2"))
                        h2 = SubElement(sub_element, "h2", id="ch" + str(level1) + "-s" + str(level2_counter),
                                        attrib={"xml:space": "preserve"},
                                        smilref=str(qec(attribs["Title"])) + ".smil#ch" + str(level1) + "-s" + str(
                                            level2_counter))
                        h2.text = e[1]
                        current_level = "level2"
                        level2_list.append(sub_element)
                        level3_counter = 0
                        fill_in_page_text(ncx, smil, xml, i, ["level2", level2_list, level2], attribs)

                    if e[0] == "level3":
                        level3 += 1
                        level3_counter += 1
                        if current_level == "level1" or current_level == "" or (
                                current_level == "level3" and len(level2_list) < 1):
                            sub_element = SubElement(level1_list[level1], "level3", id=qec("level3"))
                        else:
                            sub_element = SubElement(level2_list[level2], "level3", id=qec("level3"))
                        h3 = SubElement(sub_element, "h3",
                                        id="ch" + str(level1 - 1) + "-s" + str(level2_counter) + "-ss" + str(
                                            level3_counter),
                                        attrib={"xml:space": "preserve"},
                                        smilref=str(qec(attribs["Title"])) + ".smil#ch" + str(level1 - 1) + "-s" + str(
                                            level2_counter) + "-ss" + str(level3_counter))
                        h3.text = e[1]
                        level3_list.append(sub_element)
                        current_level = "level3"
                        fill_in_page_text(ncx, smil, xml, i, ["level3", level3_list, level3], attribs)

                except IndexError:
                    continue
        else:
            if current_level == "level1":
                fill_in_page_text(ncx, smil, xml, i, [current_level, level1_list, level1], attribs)
            elif current_level == "level2":
                fill_in_page_text(ncx, smil, xml, i, [current_level, level2_list, level2], attribs)
            elif current_level == "level3":
                fill_in_page_text(ncx, smil, xml, i, [current_level, level3_list, level3], attribs)

        for j in range(0, len(pages[i])):
            text = pages[i][j]
            if text.__contains__("■"):
                try:
                    for e in tag_dict.keys():
                        if tag_dict[e][0][1].lower() == (pages[i][j - 1] + text).replace("■ ", "").lower().strip():
                            pages[i][j - 1] = ""
                            text = ""
                    if text != "":
                        pass
                except IndexError:
                    pass
            # else:
            #     if current_level == "level1":
            #         p = SubElement(xml.findall(".//level1")[level1],"p", attribs={"xml:space":"preserve"}, id=qec("p"))
            #         span = SubElement(p,"span", attrib= {"class":"text"}, id=get_element_count("span"), smilref=str(qec(attribs["Title"]))+".smil#"+qec("span"))
            #         span.text = text


def run(**attribs):
    global dc_metadata, dtb_metadata, ncx_smil_metadata, tag_dict  # pages, tag_dict
    req = required_attribs(dc=True, dtb=True, nav=True, ncx_smil=True, smil=True)
    for r in req:
        if r not in attribs.keys():
            print(r)
            raise ValueError("Missing required arguments for ncx file. \nRequired arguments are:" + str(req))

    ncx = start_ncx_file(attribs=attribs)
    smil = start_smil_files(attribs=attribs)
    xml = start_xml_file(attribs=attribs)

    ncx_starting_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<!DOCTYPE html PUBLIC>']
    smil_starting_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<!DOCTYPE smil PUBLIC>']
    xml_starting_lines = ['<?xml version = "1.0" encoding = "UTF-8"?>',
                          '<?xml-stylesheet type = "text/css" href = "daisy.css" media = "screen" ?>',
                          '<?xml-stylesheet type = "text/xsl" href = "daisyTransform.xsl" media = "screen" ?>',
                          '<!DOCTYPE dtbook SYSTEM "dtbook-2005-3.dtd">']
    fill_in_tags(ncx, smil, xml, attribs)
    write_file(attribs["Title"], ".ncx", ncx_starting_lines, ncx)
    write_file(attribs["Title"], ".smil", smil_starting_lines, smil)
    write_file(attribs["Title"], ".xml", xml_starting_lines, xml)


pdf = PdfFileReader(open('/Users/rosie/Ben_Stuff/Sedgewick_ALGORITHMS_ED4_3513.pdf', 'rb'))
max_pg = pdf.getNumPages()

with open('tag_dict.pickle', 'rb') as handle:
    tag_dict = pickle.load(handle)
with open('pages.pickle', 'rb') as handle:
    pages = pickle.load(handle)
run(Title="Title", Creator=["Jane Doe", "Arnold", "Karen"], Publisher="Publisher", Date="2018", depth=0,
    Identifier="12341234", Format="Default",
    Language="EN", maxPageNumber=0, multimediaType="text", multimediaContent="text", totalPageCount=0,
    totalTime="00:00:00", uid="12341234", id="12341234", totalElapsedTime=0)
