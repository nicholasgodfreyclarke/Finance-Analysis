__author__ = 'nicholasclarke'

# Requires Firefox to be installed.

from sys import argv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import glob

current_dir = os.path.dirname(os.path.realpath(__file__))

newpath = current_dir + "/estatements2"
if not os.path.exists(newpath):
    os.makedirs(newpath)

#print "python \"" + current_dir + "/Download_Estatements.py\" " + newpath

#os.system("python \"" + current_dir + "/Download_Estatements.py\" " + "\"" + newpath + "\"")

#download_folder = argv[1]

download_folder = newpath

#Enter login details here.
registration_number = ''
pac_number = ''
phone_number_last_four = ''

#Set up automatic downloading (as pdf) so we don't have to interact with the os
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)  # The 2 parameter sets a custom download dir
fp.set_preference("browser.download.manager.showWhenStarting", False)
fp.set_preference("browser.download.dir", download_folder)  # Set the download dir here
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

browser = webdriver.Firefox(firefox_profile=fp)

#Navigate to AIB login page
browser.get("https://aibinternetbanking.aib.ie/inet/roi/login.htm")

#Enter in registration number and go to next page
browser.find_element_by_name('regNumber').send_keys(registration_number + Keys.RETURN)

#Determine order of pac numbers to be inputted
digits = list()
strong_tags = browser.find_elements_by_tag_name('strong')
for element in strong_tags:
    if element.text[0:5] == 'Digit':
        digits += (str(element.text[-1]),)

#Input pac numbers
browser.find_element_by_id('digit1').send_keys(pac_number[int(digits[0])-1])
browser.find_element_by_id('digit2').send_keys(pac_number[int(digits[1])-1])
browser.find_element_by_id('digit3').send_keys(pac_number[int(digits[2])-1])

#Input last four digits of phone number and got to next page
browser.find_element_by_id('challenge').send_keys(phone_number_last_four + Keys.RETURN)

browser.find_element_by_xpath("//input[@value='Statements & Advices']").click()
browser.find_element_by_xpath("(//input[@name='tabName'])[3]").click()
browser.find_element_by_name("vieweStatements").click()

option_list = list()

#Create a list of every month on record
for option in browser.find_element_by_id('selectedDate').find_elements_by_tag_name('option'):
    option_list += (option.text,)

i = 0
download_count = 0
# Loop through every month and download every statement
for j in range(len(option_list)):
    el = browser.find_element_by_id('selectedDate')
    for option in el.find_elements_by_tag_name('option'):
        if option.text == option_list[i]:
            option.click()
            #Download every statement within each month
            for k in browser.find_elements_by_class_name('aibLinkStyle01'):
                if k.text == "Save":
                    k.click()
                    download_count += 1
            i += 1
            break

# Wait for files to finish downloading
while len(glob.glob1(newpath,"*.part")) != download_count:
    pass

browser.quit()


