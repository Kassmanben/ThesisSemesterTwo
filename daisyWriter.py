import xml
import xml.etree.cElementTree as ET
from xml.dom import minidom

filename = "test.xml"


def write_meta_tag(content=None, name=None, httpequiv=None):
    meta_str = "<meta"
    if content:
        meta_str += "\tcontent=\"" + str(content) + "\""
    if name:
        meta_str += "\tname=\"" + str(name) + "\""
    if httpequiv:
        meta_str += "\thttp-equiv=\"" + str(httpequiv) + "\""

    meta_str += "/>"
    return meta_str


def fill_in_non_ET_Things(file, ol=[], mt=[]):
    f = open(file, "r")
    f_str = ""
    for l in ol:
        f_str += l + "\n"
    for fl in f.readlines():
        print(fl)
        if fl.__contains__("<head/>"):
            f_str += "<head>"
            for m in mt:
                f_str += m + "\n"
            f_str += "</head>"
        else:
            if fl.__contains__('<?xml version="1.0" ?>'):
                continue
            f_str += fl

    f.close()
    f = open(file, "w")
    f.write(f_str)
    f.close()


dtbook = ET.Element("dtbook", xmlns="http://www.daisy.org/z3986/2005/dtbook/", attrib={"xml:lang": "en"},
                    version="2005-3")
head = ET.SubElement(dtbook, "head")
meta1 = ET.SubElement(head, "meta", content="text/html; charset=utf-8", attrib={'http-equiv':"default-style"})
meta2 = ET.SubElement(head, "meta", name="dtb:uid", content="9781119284512")
meta3 = ET.SubElement(head, "meta", name="dc:Identifier", content="9781119284512")
meta4 = ET.SubElement(head, "meta", name="dc:Title",
                     content="Combustion Engines: An Introduction to Their Design, Performance, and Selection")
meta5 = ET.SubElement(head, "meta", name="dc:Creator", content="Aman Gupta, Shubham Sharma, Sunny Narayan")
meta6 = ET.SubElement(head, "meta", name="dc:Description",
                      content="Vehicle noise, vibration, and emissions are only a few of the factors that can have a detrimental"
                              " effects on overall performance of an engine.  These aspects are benchmarks for choice of customers "
                              "while choosing a vehicle or for engineers while choosing an engine for industrial applications.  "
                              "It is important that mechanical and automotive engineers have some knowledge in this area, "
                              "as a part of their well-rounded training for designing and selecting various types of engines.   "
                              "This volume is a valuable introductory text and a handy reference for any engineer, manager, or "
                              "technician working in this area.  The automotive industry, and other industries that make use of "
                              "engines in their industrial applications, account for billions, or even trillions, of dollars of "
                              "revenue worldwide and are important in the daily lives of many, if not most, of the people living "
                              "on this planet.   This is an area that affects a staggering number of people, and the information "
                              "needed by engineers and technicians concerning the performance of various types of engines is of "
                              "paramount importance in designing and selecting engines and the processes into which they are introduced.")
meta7 = ET.SubElement(head, "meta", name="dc:Format", content="ANSI/NISO Z39.86-2005")
meta8 = ET.SubElement(head, "meta", name="dc:Publisher", content="Bookshare")
meta9 = ET.SubElement(head, "meta", name="dc:Language", content="en")


book = ET.SubElement(dtbook, "book", id="book_73036475070",
                     attrib={'xmlns:epub': "http://www.idpf.org/2007/ops", 'epub:type': "frontmatter"})

xmlstr = minidom.parseString(ET.tostring(dtbook)).toprettyxml(indent="   ")
with open(filename, "w") as f:
    f.write(xmlstr)

# DO LAST, SINCE ELEMENTTREE WORKS ONLY ON XML
opening_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<?xml-stylesheet type="text/css" href="daisy.css" media="screen" ?>',
                 '<?xml-stylesheet type="text/xsl" href="daisyTransform.xsl" media="screen" ?>',
                 '<!DOCTYPE dtbook SYSTEM "dtbook-2005-3.dtd">']
# fill_in_non_ET_Things(filename, ol=opening_lines, mt=meta_tags)
