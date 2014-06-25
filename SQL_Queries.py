__author__ = 'nicholasclarke'

import sqlite3

def query(sql_string):

    conn = sqlite3.connect('AIB_Database.db')

    c = conn.cursor()

    # Create table
    c.execute(sql_string)

    for row in c.fetchall():
        print row

    conn.close()