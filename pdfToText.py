import PyPDF2
import pickle

pdfFileObj = open('/Users/Ben/Downloads/Sedgewick_ALGORITHMS_ED4_3513.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

correct_text_by_page = {}

min_pg = 11
max_pg = 13

for pg_num in range(min_pg, max_pg):
    pageObj = pdfReader.getPage(pg_num)
    page_text = pageObj.extractText()
    page_text = page_text.replace("\n", " ")
    correct_text_by_page[pg_num+1] = page_text

for page in correct_text_by_page.keys():
    print(correct_text_by_page[page])

with open('correct_text_by_page.pickle', 'wb') as handle:
    pickle.dump(correct_text_by_page, handle, protocol=pickle.HIGHEST_PROTOCOL)
