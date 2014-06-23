Finance-Analysis
================

Project to download historical estatements from AIB, parse the pdfs into csv and perform analysis on the results.

Requirements:
Firefox
Selenium package
pdfminer package
numpy package

Four stages:

1.  Download_Estatements.py

    Log into AIB, navigate to estatement records and download all available.

    Usage:

    AIB requires login information so they are passed by command line arguments.
    
    python Download_Estatements.py registration_number pac_number phone_number_last_four

    Example:
    python Download_Estatements.py 34556622 8923 0192

2.  Parse_Pdf.py

    Parse the downloaded estatement pdfs into XML (to retain the most information about character position, relationships).

3.  XML_To_CSV.py

    Parse the XML into csv separating out the data into the required columns.

4.  Analysis.py

    Create summary statistics (group by expense type, rank by magnitude, etc) and visualise using mathlibplot.
    This is yet to be started.