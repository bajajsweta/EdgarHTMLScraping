
# coding: utf-8

# ### EDGAR HTML SCRAPING

# ## Import All the Packages

# In[38]:

import requests
from bs4 import BeautifulSoup
import pandas
import os
import zipfile
import boto
from boto.s3.connection import S3Connection
import tinys3
import sys


# ## Enter the Inputs from User

# In[47]:

def user_input_cik_validation(value):
    while True:
        try:
            cik_input = int(input(value))
            if value in range(0,1000000):
                print(True)
                print("Valid Key") 
                continue
                #try again... Return to the start of the loop
        except ValueError:
            print("Sorry, Incorrect cik! Please provide a valid cik 123")
            #try again... Return to the start of the loop
            continue
        else:
            #cik was successfully parsed!
            #we're ready to exit the loop.
            break
    return value



try:
    cik_input_validate = user_input_cik_validation("cik:") 
    if not cik_input_validate:
        raise ValueError('empty string')
except ValueError as e:
    print(e)


# In[ ]:

# cik_input = input('cik: ')
accession_input = input('accession_number: ')
aws_key = input('aws Key: ')
aws_secret_key = input('aws secret key: ')


# ## Generate the URL to be Accessed

# In[40]:

Firstpage = requests.get("https://www.sec.gov/Archives/edgar/data/"+ str(cik_input) + "/" + str(accession_input) + "/" + str(accession_input[:10]) + "-" + str(accession_input[10:12]) + "-" + str(accession_input[12:]) + "-index.html")
print (Firstpage)
soup1 = BeautifulSoup(Firstpage.text)


# In[41]:

tables_all = soup1.find("table", {"class":"tableFile","summary":"Document Format Files"})
len(tables_all)


# ## Find the correct 10K/10Q File to be loaded

# In[42]:

link = tables_all.find('a')
href_value = link.get('href')
href_value


# In[ ]:

page = requests.get("https://www.sec.gov" + href_value)

soup = BeautifulSoup(page.text)


# In[44]:

def parse_table(table):
    """ Get data from table """
    for row in table.find_all('tr'):
        if "##cceeff" in row:
               return True
        else:
               return False
        


# In[45]:

href_for_10q_10K = href_value[-15:]
href_for_10q_10K


# ## Find the correct tables for 10K/10Q File to be loaded

# In[ ]:

if '10q' in href_for_10q_10K:
    tables = soup.find_all("table", border=1)
    j = 0
    for table in tables:
        data = []
        name = 'tables'+str(j)+'.csv'
        j+=1

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [(''.join(ch.strip('[\n,$]') for ch in ele.text)).strip() for ele in cols]
            data.append([ele for ele in cols if ele])
            t = pandas.DataFrame(data)
            t.to_csv(name,encoding='utf-8')
else:
    data1 = []
    tables2 = soup.find_all("table")
    k = 0
    while k < len(tables2):
        table_check = parse_table(tables2[k])
        if table_check == True:
            #k = 0
            for table in tables2:
                columns = table.find_all('td')
                for column in columns:
                    if column.text.find("$") > -1 or column.text.find("%") > -1:
                        data1.append(table)
                        break


# ## Get the List of Files from the Current Directory

# In[ ]:

#Get the List of Files from the Current Directory
content_list = []

for content in os.listdir("."): # "." means current directory
    if content.endswith(".csv"):
        content_list.append(content)

print (content_list)


# ## Move the Files to a Zip File

# In[ ]:

ZipFile = zipfile.ZipFile("zip_csv_folder.zip", "w" )

for a in content_list:
    #ZipFile.write(os.path.basename(a), compress_type=zipfile.ZIP_DEFLATED)
    ZipFile.write(a)


# ## First Create the Bucket and Check if It Exists or No

# In[ ]:

#Connection for Boto
# conn = S3Connection('AKIAJW7GUWVQDH7OGRVA', 'YCGmOrYtjkuuV8KTeqmBTF+oOHBZFnDmBdmSnWdM')
conn = S3Connection(aws_key, aws_secret_key)


# In[ ]:

#Create a Bucket and Check if Bucket Exists or No
bucket = conn.lookup('some-value')
if bucket is None:
    print ("This bucket doesn't exist.")
    bucket = conn.create_bucket('bucket-csvs')
    print ("Bucket Created")
#     Else if bucket is there and use that bucket


# In[ ]:

bucketobj = conn.get_bucket(bucket)
bucketobj


# In[ ]:

#Create tinys3 Connection
connt3 = tinys3.Connection(aws_key,aws_secret_key,tls=True)


# ## Get the Zip File from the Current Directory and Upload it on AmazonS3

# In[ ]:

#Example #f = open('H:/Advance Data Science/Assignment - 1/R/csv1.zip','rb')

f = open(os.getcwd() + '/zip_csv_folder.zip','rb')
connt3.upload('zip_csv_folder.zip',f,'bucket-csvs')

