import datetime
import inspect
from xml.dom import minidom
from xml.etree.cElementTree import *

filename = "test.xml"

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
smil_metadata = {"id": "REQUIRED", "defaultState": 'false', "override": 'hidden', "bookStruct": "PAGENUMBER"}


def make_ncx_meta_tags(head_elem, l):
    for e in l.keys():
        if l[e] is not None and e in nav_metadata.keys():
            prefix_e = "dtb:" + e
            meta_elem = SubElement(head_elem, "meta", name=prefix_e, content=str(l[e]))


def required_attribs(dc=False, dtb=False, smil=False, nav=False):
    global dc_metadata, dtb_metadata, smil_metadata
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
    return required_args


def make_ncx_file(**attribs):
    global dc_metadata, dtb_metadata, smil_metadata
    req = required_attribs(dc=True, dtb=True, nav=True, smil=True)
    print(req)
    for r in req:
        if r not in attribs.keys():
            print(r)
            raise ValueError("Missing required arguments for ncx file. \nRequired arguments are:" + str(req))

    filename = attribs["Title"] + ".ncx"

    ncx = Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1", attrib={"xml:lang": "eng"})
    head = SubElement(ncx, "head")

    smilCustomTest = SubElement(head, "smilCustomTest")
    for s in smil_metadata.keys():
        try:
            smilCustomTest.set(s, attribs[s])
        except KeyError:
            smilCustomTest.set(s, smil_metadata[s])

    make_ncx_meta_tags(head, attribs)

    xmlstr = minidom.parseString(tostring(ncx)).toprettyxml(indent="     ")

    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?')
        f.write('<!DOCTYPE html PUBLIC')
        f.write(xmlstr)


make_ncx_file(Title="Title", Publisher="Publisher", Date="2018", depth=0, Identifier="12341234", Format="Default",
              Language="EN", maxPageNumber=0, multimediaType="text", multimediaContent="text", totalPageCount=0,
              totalTime="00:00:00", uid="12341234", id="12341234")
# 
# opening_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
#                  '<?xml-stylesheet type="text/css" href="daisy.css" media="screen" ?>',
#                  '<?xml-stylesheet type="text/xsl" href="daisyTransform.xsl" media="screen" ?>',
#                  '<!DOCTYPE dtbook SYSTEM "dtbook-2005-3.dtd">']
# # fill_in_non_ET_Things(filename, ol=opening_lines, mt=meta_tags)
