# coding=utf-8
__author__ = 'nicholasclarke'
#!/usr/bin/python

import os
import xml.etree.ElementTree as ET
import re
import numpy as np
from datetime import datetime
import sqlite3
import csv

def Parse_XML(xml_file, output_type,account_name):

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
        """
        Sort strings into relevant columns - Date, Details, Debit, Credit
        """

        catagories = {'Date':list(), 'Details':list(), 'Debit €':list(), 'Credit €':list(), 'Balance €':list()}

        anchors = column_anchors(string_data)

        transaction_pattern = re.compile('\d{1,5}.\d{2}')

        monetary_admissable_list = list()
        
        # Collect all monetary transaction amounts - Debit, Credit, Balance
        for candidate in string_data:
            if candidate[1] > anchors['Debit €']['hor_start'] and candidate[2] < anchors['Details']['ver_start'] \
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

                print 'Categorisation error: ' + str(candidate)
                print xml_file

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
        # Now to just clean up the Details column, remove text at the bottom of the page from Details
        for string in catagories['Balance €']:
            if string[2] < lower_bound:
                lower_bound = string[2]
        catagories['Details'] = [x for x in catagories['Details'] if not x[2] < lower_bound]

        return catagories

    def convert_dates(categories):
        """
        Convert dates from the 1 Jun 2014 format to the YYYY-MM-DD sqlite3 compatible date format.
        """
        for date in catagories['Date']:

            date[0] = datetime.strptime(date[0], '%d %b %Y').strftime('%Y-%m-%d')

        return catagories

    def sorted_details_array(categories):
        """
        There are no null values in the Details columns, so:
        first: sort details by page,ver_start position
        second: insert into numpy array
        third fit other columns to it (they will have the same ver_start pos as they are the same row) - is this robust?
        """

        numpy_fields = [('Value','S30'), ('vert_start',float), ('page_no',int)]

        # multiply vert_start * -1 to get correct sorting behaviour (vert_start is from bottom of page)
        details_data = [[x[0],] + [-1 * float(x[2]),] + [x[5],] for x in catagories['Details']]

        np_sort_array = np.array([(a,b,c) for (a,b,c) in details_data], dtype=numpy_fields)

        np_sort_array = np.sort(np_sort_array, order=['page_no', 'vert_start',])

        return np_sort_array

    def final_array(sorted_details_array, catagories):

        numpy_fields = [('Date','S30'), ('Details','S30'), ('Debit €', float), ('Credit €', float),('Balance €',float),
                        ('vert_start',float), ('page_no',int)]
        output_array = np.zeros(sorted_details_array.shape[0],dtype = numpy_fields)

        # Fill in details
        for i in range(sorted_details_array.shape[0]):
            output_array['Details'][i] = sorted_details_array[i][0]
            output_array['vert_start'][i] = sorted_details_array[i][1]
            output_array['page_no'][i] = sorted_details_array[i][2]

        def fill_array(column):
            """
            Fill in date, debit, credit, balance
            Check that they have the same vertical height and page no as the details
            """
            for i in range(sorted_details_array.shape[0]):
                for string_info in catagories[column]:
                    if -1 * string_info[2] == output_array['vert_start'][i] and string_info[5] == output_array['page_no'][i]:
                        output_array[column][i] = string_info[0]

        fill_array('Date')
        fill_array('Debit €')
        fill_array('Credit €')
        fill_array('Balance €')

        # Associate a date with each row for analysis
        current_date = ''
        for row in range(output_array.shape[0]):
            if output_array['Date'][row] != '':
                current_date = output_array['Date'][row]
            else:
                output_array['Date'][row] = current_date

        # Delete row with superfluous data (exchange rates, atm withdrawal times, etc)
        delete_row_list = list()
        for row in range(output_array.shape[0]):
            if output_array['Debit €'][row] == 0 and output_array['Credit €'][row] == 0:
                delete_row_list += (row,)
        output_array = np.delete(output_array,delete_row_list,0)

        return output_array

    def insert_into_database(output_data):

        conn = sqlite3.connect('AIB_Database.db')

        c = conn.cursor()

        sql_update_data = list()

        for row in output_data:
            sql_update_data += ([row[0],row[1],row[2],row[3],row[4], account_name,row[3]-row[2]],)

        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS Transactions
                     (Date text, Details text, Debit real, Credit real, Balance real, Net_Transaction real, Account_Name text)
                     ''')

        c.executemany('INSERT INTO Transactions VALUES (?,?,?,?,?,?,?)', sql_update_data)

        conn.commit()

        conn.close()

    print "Parsing " + xml_file + " to " + output_type

    string_data = extract_string_coordinates(xml_file)

    catagories = Catagorise(string_data)

    catagories = convert_dates(catagories)

    details_array = sorted_details_array(catagories)

    output_data = final_array(details_array, catagories)

    if output_type == 'csv':
        with open('Estatements.csv','a') as f:
            writer = csv.writer(f)
            for row in output_data:
                # Use round due to how floats are stored in numpy
                writer.writerow([row[0],row[1],round(row[2],2),round(row[3],2),round(row[4],2), account_name,round(row[3]-row[2],2)])
    else:
        insert_into_database(output_data)

    print "Finished!"


if __name__ == '__main__':
    import sys
    xml_filenames = []
    if len(sys.argv) <= 3:
        exit('Requires a XML file or directory as argument, output type (csv/db) and account name')

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

    output_type = sys.argv[2]
    if output_type != 'csv' and output_type != 'db':
        exit('Please specify output as csv/db')

    account_name = sys.argv[3]

    for xml_file in xml_filenames:
        Parse_XML(xml_file,output_type,account_name)
