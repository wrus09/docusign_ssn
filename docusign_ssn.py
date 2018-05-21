from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import credentials as creds
import glob
import os
import csv
import pandas as pd
from pandas import Series,DataFrame
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Test URL https://na8.salesforce.com/a45C0000000EtIP
url = sys.argv[1] # Takes the 2nd argument given on run prompt (1st is always the file name)
driver = webdriver.Chrome('/Users/wrus/Python_Files/chromedriver_2')

# Login to salesforce
driver.get(url)
time.sleep(1)
driver.find_element_by_xpath('//*[@id="username"]').send_keys(creds.sf_username)
driver.find_element_by_xpath('//*[@id="password"]').send_keys(creds.sf_password)
driver.find_element_by_xpath('//*[@id="Login"]').click()

# NOTE: Must Authenticate Manually at this point due to security restrictions
for i in range (15,0,-1):
    print('Ya got ' + str(i) + ' seconds to authenticate, bro.') # removed ,end='\r' for python 2
    time.sleep(1)


driver.find_element_by_xpath('//*[@id="tryLexDialogX"]').click() # Close lightning pop up


# Get Envelope ID from link
driver.get(url)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/table/tbody/tr/td[2]/div[4]/div[1]/table/tbody/tr/td[2]/input[4]').click()
envelopeid = driver.find_element_by_xpath('//*[@id="00NC0000006SaQo"]')
envelopeid = str(envelopeid.get_attribute('value'))
doc_url = 'https://app2.docusign.com/documents/details/'+envelopeid
print('Got Docusign Link: ' + doc_url)

# Get CSV from docusign.com
driver.get(doc_url)
driver.find_element_by_xpath('//*[@id="username"]').send_keys(creds.sf_username)
driver.find_element_by_xpath('/html/body/div/div/div/main/section/div[1]/div/form/div[3]/button').click()
driver.find_element_by_xpath('//*[@id="password"]').send_keys(creds.sf_password)
driver.find_element_by_xpath('/html/body/div/div/div/main/section/div[1]/div/form/div[4]/button').click()

# Wait for stupid slow docusign page to load
for i in range (32,0,-1):
    time.sleep(1)
    print('Waiting ' + str(i) + ' seconds to continue...') # removed ,end='\r' for python 2

driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div/div[1]/div[1]/div/div[1]/div/div[1]/div/div[2]/div[1]/div/button[2]').click() # More dropdown
driver.find_element_by_xpath("//*[contains(text(), 'Form Data') and contains(@type, 'button')]").click() # Form Data option
# driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div/div[1]/div/div[1]/div/div[2]/div[1]/div/button[2]').click()
# driver.find_element_by_xpath('//*[@id="menu-button-"]/ul/li[3]').click()
time.sleep(2)
driver.find_element_by_xpath('//*[@id="ng-app"]/body/envelopes-form-data-window/div/form/div[4]/a').click() # Download Button


# Get SSN from Docusign Form Data csv
list_of_files = glob.glob('/Users/wrus/Downloads/*.csv')
latest_file = max(list_of_files, key=os.path.getctime)
print('Got latest file: ' + latest_file)
df = pd.read_csv(latest_file,error_bad_lines=False)
df = df.set_index('Field')
SSN = df.loc['Owner 1 Social Sn','Value']



if str(SSN) == 'nan':
    print('Daaaaaaang no sosh! All I got was "' + str(SSN) + '"')
elif len(SSN) != 11:
    print('Dis sosh aint lookin so good... does this look right to you? ' + str(SSN))
else:
    print('Got dem diggiezzzz')
    driver.get(url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[contains(@id,"lookup001C000001")]').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="RecordType_ileinner"]/a').click()

    driver.find_element_by_xpath('//*[@id="p3"]').click()
    driver.find_element_by_xpath('/html/body/div/div[3]/table/tbody/tr/td[2]/form/div/div[2]/div[2]/table/tbody/tr[3]/td[2]/div/select/option[2]').click()
    driver.find_element_by_xpath('/html/body/div/div[3]/table/tbody/tr/td[2]/form/div/div[3]/table/tbody/tr/td[2]/input[1]').click()
    time.sleep(1)
    ssn_field = driver.find_element_by_xpath('//*[@id="00NC0000006aac6"]')
    ssn_field.send_keys(SSN)
    #CLICK SAVE driver.find_element_by_xpath('/html/body/div[1]/div[3]/table/tbody/tr/td[2]/form/div/div[1]/table/tbody/tr/td[2]/input[1]').click()
    os.remove(latest_file) # Deletes CSV
    print('Finished Successfully!!!!!')

driver.quit()
