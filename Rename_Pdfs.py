__author__ = 'nicholasclarke'

import os

os.chdir('/Users/nicholasclarke/Code/PycharmProjects/AIB project/estatements')

[os.rename(f, f.replace('.part', '')) for f in os.listdir('.')]
