import io

import PyPDF2
import wand
import wand.image
from wand.color import Color


def pdf_page_to_png(src_pdf, pagenum = 0, resolution = 72,):
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

    img = wand.image.Image(file = pdf_bytes, resolution = resolution)
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
    img = pdf_page_to_png(src_pdf, pg_num, resolution = 300)
    img.save(filename = big_filename)