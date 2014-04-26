# coding=utf-8
__author__ = 'nicholasclarke'
#!/usr/bin/python

import re
import csv
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
import numpy as np

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

for i in Date:
    Details += [[i[0][11:],] + i[1:],]

print Details
fields = [('Value','S20'), ('hor_start',float), ('vert_start',float), ('hor_end',float), ('vert_end',float)]
# dtype = [('name', 'S10'), ('height', float), ('age', int)]
Details_array = np.array(Details, dtype=fields)
# np.dtype([('R','u1'), ('G','u1'), ('B','u1'), ('A','u1')])
# print np.sort(Details_array, order = 'hor_start')

print Details_array
with open('test.csv','wb') as f:
    writer = csv.writer(f)
    for i in Details:
        writer.writerow(i)

#
# # Obtain the height of the data by subtracting the ending vertical coordinate of a character
# # from it's starting vertical coordinate.
# # Look at this fucking hackery... (I think I have a problem with dictionaries and trying to use them as lists)
# height = Date[Date.keys()[0]][3] - Date[Date.keys()[0]][1]
#
# test = OrderedDict(sorted(Date.items(), key=lambda t: t[1], reverse=True))
#
#
#
# print test
#
# print "\n"*10
#
# print test['14 Feb 2014 BALANCE FORWARD']
#
# print test['17 Feb 2014 Interest Rate']
#
# print test['14 Feb 2014 BALANCE FORWARD'][3] - test['17 Feb 2014 Interest Rate'][1]
#
# for i in test:
#     Details[i[11:]] = Date[i]
#
# Ordered_Details = OrderedDict(sorted(Details.items(), key=lambda t: t[1], reverse=True))
#
#
# # If it's within half the height it should be admissible
#
# #Okay, better idea. Create the details row and then fit the other rows to it!
# #First separate out dates, and make into correct format
#
# # Can't use dicts because of duplication in keys!