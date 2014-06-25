# coding=utf-8
__author__ = 'nicholasclarke'
#!/usr/bin/python

import csv
import os
import xml.etree.ElementTree as ET
import numpy as np
from datetime import datetime
import StringIO
import re
import pprint

# Highly recommend pprint for debugging here.

def Parse_XML(xml_file):

    def extract_string_coordinates(xml_file):
        """
        Takes xml file as input and outputs a tuple of tuples consisting of the contiguous strings and their coordinates.
        The coordinate system:
        First coordinate: starting horizontal position of character (from left)
        Second coordinate: Starting vertical position of character (from bottom)
        Third coordinate: Ending horizontal position of character (from left)
        Fourth coordinate: Ending vertical position of character (from bottom)
        """

        tree = ET.parse(xml_file)
        root = tree.getroot()

        #Determine the number of pages
        number_of_pages = 0
        for child in root.findall("./page"):
            number_of_pages += 1

        # string_data will hold the value of the string and it's four coordinates.
        string_data = tuple()

        for page in range(1, number_of_pages + 1):

            for child in root.findall("./page[" + str(page) + "]/textbox/textline"):

                # Each character has an individual position, but I'll use the
                # position of the first character as a proxy for the position of the word.
                string_coordinate = child.find("./text").attrib['bbox']

                characters = ""
                # Gather characters of string
                for grandchild in child.findall("./text"):
                    characters += grandchild.text

                # Store the string, it's coordinates and the page number.
                string_data += ([characters[:-1].encode(encoding='UTF-8'),] + [float(i) for i in string_coordinate.split(",")] + [page,],)

        return string_data

    def number_of_pages(xml_file):

        tree = ET.parse(xml_file)
        root = tree.getroot()

        #Determine the number of pages
        number_of_pages = 0
        for child in root.findall("./page"):
            number_of_pages += 1

    def column_anchors(string_data):
        """
        Collect the coordinates of the (known) column headers for use in column classification.
        """
        anchor_coordinates = dict.fromkeys(['Date', 'Details', 'Debit €', 'Credit €', 'Balance €'])

        for candidate in string_data:
            if candidate[0] in anchor_coordinates.keys():
                anchor_coordinates[candidate[0]] = {'hor_start':candidate[1], 'hor_end':candidate[3],
                                                    'ver_start':candidate[2], 'ver_end':candidate[4]}

        return anchor_coordinates

    def Catagorise(string_data):

        catagories = {'Date':list(), 'Details':list(), 'Debit €':list(), 'Credit €':list(), 'Balance €':list()}

        anchors = column_anchors(string_data)

        transaction_pattern = re.compile('\d{1,5}.\d{2}')

        monetary_admissable_list = list()
        
        # Collect all monetary transaction amounts - Debit, Credit, Balance
        for candidate in string_data:
            if candidate[1] > anchors['Details']['hor_end'] and candidate[2] < anchors['Details']['ver_start'] \
                    and transaction_pattern.match(candidate[0]):
                monetary_admissable_list += (candidate,)
        
        # Further subdivide into Debit, Credit, Balance
        for candidate in monetary_admissable_list:

            # Balance
            if anchors['Balance €']['hor_start'] < candidate[1]:
                catagories['Balance €'] += (candidate,)

            # Debit
            elif anchors['Debit €']['hor_start'] < candidate[1] < anchors['Credit €']['hor_start']:
                catagories['Debit €'] += (candidate,)

            # Credit
            elif anchors['Credit €']['hor_start'] < candidate[1] < anchors['Balance €']['hor_start']:
                catagories['Credit €'] += (candidate,)

            else:
                print 'Categorisation error: ' + candidate

        date_pattern = re.compile("\d{1,2}\s\w{3}\s\d{4}")

        # Details Column
        for candidate in string_data:
            if anchors['Date']['hor_end'] < candidate[1] < anchors['Debit €']['hor_start'] and candidate[2] < anchors['Date']['ver_start']:
                catagories['Details'] += (candidate,)


        # Now for Dates
        for candidate in string_data:
            if candidate[1] < anchors['Details']['hor_start'] and date_pattern.match(candidate[0]):

                # Dates and Details are sometimes concatenated so I will split them out with regex
                trimmed_date = date_pattern.search(candidate[0]).group(0)

                # Need to know where to put the decoupled details data (luckily all details have the same horizontal starting pos)
                Details_hor_start = catagories['Details'][0][1]


                catagories['Details'] += ([candidate[0][len(trimmed_date)+1:],] + [Details_hor_start,] + candidate[2:],)
                catagories['Date'] += ([trimmed_date,] + candidate[1:],)

        lower_bound = 10000
        # Now to just clean up the Details column
        for string in catagories['Balance €']:
            if string[2] < lower_bound:
                lower_bound = string[2]
        catagories['Details'] = [x for x in catagories['Details'] if not x[2] < lower_bound]

        return catagories

    def sort_numpy(categories):
        


    # Debugging

    string_data = extract_string_coordinates(xml_file)
    # for i in string_data:
    #     pprint.pprint(i)

    catagories = Catagorise(string_data)

    sort_numpy(catagories)

    # print column_anchors(string_data)


if __name__ == '__main__':
    import sys
    xml_filenames = []
    if len(sys.argv) <= 1:
        exit('Requires a XML file or directory as argument.')
    arg = sys.argv[1]
    if os.path.exists(arg) and arg.endswith('.xml'):
        xml_filenames.append(os.path.abspath(arg))
    elif os.path.exists(arg):
        all_transactions = []
        for filename in os.listdir(arg):
            if filename.endswith('.xml'):
                xml_filenames.append(os.path.join(os.path.abspath(arg), filename))
    else:
        exit('Invalid XML file or no such file or directory.')

    for xml_file in xml_filenames:
        Parse_XML(xml_file)
    # for xml_file in xml_filenames:
    #     csv_data = XML2CSV(xml_file)
    #     print csv_data
