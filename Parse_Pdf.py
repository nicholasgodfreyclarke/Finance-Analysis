__author__ = 'nicholasclarke'

import os
import sys
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter
from pdfminer.layout import LAParams

def parse_pdfs(pdf_filenames):
    # Set parameters
    pagenos = set()
    maxpages = 0
    password = ''
    imagewriter = None
    codec = 'utf-8'
    caching = True
    laparams = LAParams()

    rsrcmgr = PDFResourceManager(caching=caching)

    # Convert to XML as it retains the most information about text position (compared to text, html, etc).
    for pdf_file in pdf_filenames:

        print "Converting %s to xml."%pdf_file

        fname, ext = os.path.splitext(pdf_file)
        outfile = fname + '.xml'
        with open(pdf_file, 'rb') as fp, open(outfile, 'w') as outfp:

            device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                          imagewriter=imagewriter)

            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
                interpreter.process_page(page)

            device.close()

        print "Conversion complete."


if __name__ == '__main__':
    pdf_filenames = []
    if len(sys.argv) <= 1:
        exit('Requires a PDF file or directory as argument.')
    arg = sys.argv[1]
    if os.path.exists(arg) and arg.endswith('.pdf'):
        pdf_filenames.append(os.path.abspath(arg))
    elif os.path.exists(arg):
        all_transactions = []
        for filename in os.listdir(arg):
            if filename.endswith('.pdf'):
                pdf_filenames.append(os.path.join(os.path.abspath(arg), filename))
    else:
        exit('Invalid PDF file or no such file or directory.')

    parse_pdfs(pdf_filenames)