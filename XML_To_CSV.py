# coding=utf-8
__author__ = 'nicholasclarke'
#!/usr/bin/python

import csv
import os
import xml.etree.ElementTree as ET
import numpy as np
from datetime import datetime

# Brief explanation:
# I have converted the pdf into xml, pdf is a graphical format rather a textual format really
# so I have a tree of xml elements which the value of a single text character accompanied by
# their position on the page (represented by four coordinates).
# Luckily the xml is structured in that the characters of each word are all children of the same
# parent node (in most cases).

os.chdir('/Users/nicholasclarke/Code/PycharmProjects/AIB project/estatements')

tree = ET.parse("ALNqYh9w.txt")

root = tree.getroot()

data = tuple()
for child in root.findall("./page/textbox/textline"):

    value = ""

    # Each character has an individual position, but I'll use the
    # position of the first character as a proxy for the position of the word.
    coord = child.find("./text").attrib['bbox']

    # Gather characters of string
    for grandchild in child.findall("./text"):
        value += grandchild.text

    # print value, "\n", coord.split(",")

    data += ([value[:-1].encode(encoding='UTF-8'),] + [float(i) for i in coord.split(",")], )

# Anchor with Date, Details, Debit €, Credit €, Balance €

# print "hey"
# print data['Date']
# print data['Details']
# print data['Debit €']
# print data['Credit €']
# print data['Balance €']

# The coordinate system:
# First coordinate: starting horizontal position of character (from left)
# Second coordinate: Starting vertical position of character (from bottom)
# Third coordinate: Ending horizontal position of character (from left)
# Fourth coordinate: Ending vertical position of character (from bottom)

def positioning(data, x_left_bound, x_right_bound, y_top_bound, y_bottom_bound):
    """
    This function will split out the data into columns according to specified x and y spacial limits.
    """
    column = list()
    for element in data:
        if x_left_bound < element[1] < x_right_bound and y_bottom_bound < element[2] < y_top_bound:
            column += (element,)
    return column

column_identifiers = ('Date', 'Details', 'Debit €', 'Credit €', 'Balance €')

column_anchors = {}
for i in data:
    if i[0] in column_identifiers:
        column_anchors[i[0]] = i[1:]

Date = positioning(data, 0, column_anchors['Date'][0], column_anchors['Date'][1], 75)

Details = positioning(data, column_anchors['Date'][0], column_anchors['Debit €'][0], column_anchors['Date'][1], 75)

Debit = positioning(data, column_anchors['Debit €'][0], column_anchors['Credit €'][0], column_anchors['Date'][1], 75)

Credit = positioning(data, column_anchors['Credit €'][0], column_anchors['Balance €'][0], column_anchors['Date'][1], 75)

Balance = positioning(data, column_anchors['Balance €'][0], 1000000, column_anchors['Date'][1], 75)

#Split out Date from Details (they were incorrectly merged in the pdf parsing)
for i in Date:

    Details += [[i[0][11:],] + i[1:],]

    i[0] = i[0][:11]
    # Convert date to a more usable format
    d = datetime.strptime(i[0], '%d %b %Y')
    i[0] = d.strftime('%d/%m/%Y')

fields = [('Value','S30'), ('hor_start',float), ('vert_start',float), ('hor_end',float), ('vert_end',float)]

Details_array = np.array([(a,b,c,d,e) for (a,b,c,d,e) in Details], dtype=fields)

Details_array = np.sort(Details_array, order='vert_start')[::-1]

output_array = np.empty((Details_array.shape[0],5), dtype = 'S30')

for i in range(Details_array.shape[0]):
    output_array[i][1] = Details_array[i][0]

height = float(Date[0][3] - Date[0][1])

#Date
for j in range(Details_array.shape[0]):
    filled = False
    for i in Date:
        if ( Details_array[j][2] - height/2 ) < i[2] < ( Details_array[j][2] + height/2 ):
            output_array[j][0] = i[0]
            filled = True
            last_date = i[0]
    if not filled:
        output_array[j][0] = last_date # Associate each row with it's date for easier analysis

#Debit
for j in range(Details_array.shape[0]):
    filled = False
    for i in Debit:
        if ( Details_array[j][2] - height/2 ) < i[2] < ( Details_array[j][2] + height/2 ):
            output_array[j][2] = i[0]
            filled = True
    if not filled:
        output_array[j][2] = ""

#Credit
for j in range(Details_array.shape[0]):
    filled = False
    for i in Credit:
        if ( Details_array[j][2] - height/2 ) < i[2] < ( Details_array[j][2] + height/2 ):
            output_array[j][3] = i[0]
            filled = True
    if not filled:
        output_array[j][3] = ""

#Balance
for j in range(Details_array.shape[0]):
    filled = False
    for i in Balance:
        if ( Details_array[j][2] - height/2 ) < i[2] < ( Details_array[j][2] + height/2 ):
            output_array[j][4] = i[0]
            filled = True
    if not filled:
        output_array[j][4] = ""

# print output_array

with open('test.csv','wb') as f:
    writer = csv.writer(f)
    for i in output_array:
        writer.writerow(i)

#
# # Obtain the height of the data by subtracting the ending vertical coordinate of a character
# # from it's starting vertical coordinate.
# # Look at this fucking hackery... (I think I have a problem with dictionaries and trying to use them as lists)


# # If it's within half the height it should be admissible
#
# #Okay, better idea. Create the details row and then fit the other rows to it!
# #First separate out dates, and make into correct format
#
# # Can't use dicts because of duplication in keys!
# Trim leading spaces in details column