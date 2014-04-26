__author__ = 'nicholasclarke'

import os
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter #, HTMLConverter, TextConverter
from pdfminer.layout import LAParams

os.chdir('/Users/nicholasclarke/Code/PycharmProjects/AIB project/estatements')

print os.getcwd()

# Set parameters
pagenos = set()
maxpages = 0
password = ''
outfile = 'ALNqYh9w.txt'
imagewriter = None
codec = 'utf-8'
caching = True
laparams = LAParams()

rsrcmgr = PDFResourceManager(caching=caching)

outfp = file(outfile, 'w')

# Convert to XML as it retains the most information about text position (compared to text, html, etc).
device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                      imagewriter=imagewriter)

for fname in ('ALNqYh9w.pdf',):
    fp = file(fname, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp, pagenos,
                                  maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()

device.close()
outfp.close()
