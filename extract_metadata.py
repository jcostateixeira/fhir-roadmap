import os, json
import pandas as pd
import glob
import datetime


def create_current_df(path):
    if os.path.exists(path):
        df = pd.read_csv(path, sep =';', header=0).to_dict(orient="records")
        return df
    else:
        return None

def update_record(record, key, value):
#  if key in record:
    if (value != ''):
      record[key] = value
#  else:
#      record[key] = json_text.get(key)



# CSV structure: 
# idx (autoincrement index)
# Topic
# Subtopic
# Type
# Name
# Status
# URL
# FhirVersion
# Owner
# Date proposed
# Published date
# last revision date
# Maturity
# Legal Status
# Version.


def read_package(folder):
    # 2. read json files from packages - each package is a folder under packages folder
    new_files=[]
    # r=root, d=directories, f = files
    for r, d, f in os.walk(folder):
        for file in f:
            if file.endswith(".json"):
                new_files.append(os.path.join(r, file))

    result=[]
    record_upper={}
    for index, js in enumerate(new_files):
        if (js == 'packages/package.json'):
            with open(js, encoding='utf-8') as json_file:
                json_text = json.load(json_file)
             #   print(json_text)
                date = '1900' # set a old date to initialize variable and then overwrite as needed
                if('date' in json_text):
                    record_upper["pack_last_review_date"] = json_text['date']
                if('author' in json_text):
                    record_upper["pack_author"] = json_text['author']
                if('fhirVersion' in json_text) and (len(json_text['fhirVersion']) == 1) :
                    record_upper["pack_fhir_version"] = json_text['fhirVersion']
                
                if('maintainers' in json_text):
                    for m in json_text['maintainers']:
                        if ('url' in m):
                            record_upper["pack_wg_url"] = m['url']
    #print(record_upper)
    for index, js in enumerate(new_files):
        #print(js)
        if  not any(ext in js for ext in ['package-list.json',".index.json",'package.json',"validation-summary","example"]):   # for all other jsons:
         
            with open(js, encoding='utf-8') as json_file:
                 #  print(js)
                record=record_upper.copy()
                
                json_text = json.load(json_file)
               # print(json_text)
             #   print("----")
                # get the rtype (resource type) and dtype (actual detailed type)
                rtype = json_text['resourceType']

                record["id"]= json_text.get('id')

                if (rtype=="StructureDefinition"):
                    if (json_text['kind']=='logical'): # in this case, this is a logical model
                        dtype="Logical Model"
                    if (json_text['kind']=='complex-type') and (json_text['type']!='extension'): # in this case, it's a data type
                        dtype="Data type"
                    if (json_text['type']=='extension'): # in this case, it's an  extension
                        dtype="Extension"
                    if (json_text['kind']=='resource'): # in this case, it's a profile
                        dtype="Profile"
                else:
                    dtype=rtype # for other resources, the resource type is the detailed ty



            if('name' in json_text):
                name = json_text['name']
            else:
                name = ''

            if('version' in json_text):
                version = json_text['version']
            else:
                name = ''

            if('url' in json_text):
                url = json_text['url']
            else:
                url = ''

            if('date' in json_text):
                date = json_text['date'].split("T")[0]
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                date = ''

            if('status' in json_text):
                status = json_text['status']
            else:
                status = ''

            if('fhirVersion' in json_text):
                fhirVersion = json_text['fhirVersion']
            else:
                fhirVersion = ''


            update_record(record, "version", version)
            update_record(record, "name", name)
            update_record(record, "url", url)
            update_record(record, "date",date)
            update_record(record, "status", status)
            update_record(record, "type", dtype)
            update_record(record, "fhirVersion", fhirVersion)

            # CSV structure: 
            # idx (autoincrement index)
            # Topic
            # Subtopic
            # Type
            # Name
            # Status
            # URL
            # FhirVersion
            # Owner
            # Date proposed
            # Published date
            # last revision date
            # Maturity
            # Legal Status
            # Version.

            print("NEW---------------------------------")
            result.append(record)
    #print(result)
    return result

## Done. Now the logic: 
## 1. If there is a URL and that URL already exists in the csv, replace the values in the CSV  
## 2. If there is no CSV, then create a new entry with the values. Default values if not existing to ''

## Also update the data table:
# the URL for the resource is a hyperlink on the resource name - opens a new window 
# the URL for the maintainer is a hyperlink on the owner - opens a new window 


 
# save the CSV back

#df=create_current_df('resources.csv')


if os.path.exists('resources.csv'):
    df = pd.read_csv('resources.csv', sep =';', header=0).to_dict(orient="records")

n_list= read_package("packages/")
#print(n_list)

n_df=pd.DataFrame(n_list)
print(n_df)
n_df.to_csv("resources.csv")


