Finance-Analysis
================

The goal of this project is to transform AIB transactions data given in the form of pdf's into machine readable and analyis
friendly formats (csv and sqlite3 db).

The project has three main stages:

1.  Download estatments.

    Download_Estatements.py

    Log into AIB, download specified account estatement archives.

    Usage:
    python Download_Estatements.py registration_number pac_number phone_number_last_four AccountName

    Requirements: Selenium package, Firefox browser

2.  Parse PDFs to csv/sqlite3 db

    Parse_Pdf.py

    Uses PDFminer to convert the downloaded statements to XML (as this retains the most information about character
    positioning, etc)

    Usage:
    python Parse_Pdf.py DirectoryOrPDFFile

    Requirements: pdfminer package

    XML_Parser.py

    Navigates through the XML tree, uses various heuristics and regular expressions to munge the data into a
    formatted numpy array.
    It then exports the data to either a csv or database.

    Usage:
    python XML_Parser DirectoryOrPDFFile OutputType(csv/db) AccountName

    Requirements: numpy package

3.  Analysis (In progress)

    SQL_Queries.py

    A collection of sample queries for breakdown and analysis

    Plots.py

    Use mathlibplot to generate visual representation of transaction histories, trends, etc


Tested on:
Python 2.7
Mac

Thanks to Ben Murray for code review.