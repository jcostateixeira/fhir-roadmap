import os, json
import pandas as pd


# 1. Get the resources.csv - if it exists
if os.path.exists('resources.csv'):
    df = pd.read_csv('resources.csv', sep =';', header=0).to_dict(orient="records")

# 1.1 if not, create a new data frame
else:
    df = pd.DataFrame(columns=['url','id', 'rtype', 'name', 'version', 'date', 'status']).to_dict

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


# 2. read json files from packages - each package is a folder under packages folder
path_to_json = 'package/' # TO DO: instead of reading the folder package, repeat for all folders within packages/ folder
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for index, js in enumerate(json_files):
    if (js == 'package.json'):
        with open(os.path.join(path_to_json, js), encoding='utf-8') as json_file:
            json_text = json.load(json_file)

            date = '1900' # set a old date to initialize variable and then overwrite as needed
            if('date' in json_text):
                pack_last_review_date = json_text['date']
            if('author' in json_text):
                pack_author = json_text['author']
            if('fhirVersion' in json_text) and (len(json_text['fhirVersion']) == 1) :
                pack_fhir_version = json_text['fhirVersion']
            
            if('maintainers' in json_text):
                for m in json_text['maintainers']:
                    if ('url' in m):
                         pack_wg_url = m['url']
             
            
    elif (js == 'package-list.json'):
         # TO DO: do NOT process package-list.json
        print('') # do nothing ?

    else:   # for all other jsons:
        with open(os.path.join(path_to_json, js), encoding='utf-8') as json_file:
            json_text = json.load(json_file)

            # get the rtype (resource type) and dtype (actual detailed type)
            rtype = json_text['resourceType']
            if('id' in json_text):
                id = json_text['id']

            paths=[]
            if (rtype=="StructureDefinition"):
                if (json_text['kind']=='logical'): # in this case, this is a logical model
                    dtype="Logical Model"
                if (json_text['type']=='extension'): # in this case, it's an  extension
                    dtype="Extension"
                if (json_text['kind']=='resource'): # in this case, it's a profile
                    dtype="Profile"
                if (json_text['kind']=='complex-type') and (json_text['type']!='extension'): # in this case, it's a data type
                    dtype="Data type"
            else:
                dtype=rtype # for other resources, the resource type is the detailed type
            

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
                date = json_text['date']
            else:
                date = ''

            if('status' in json_text):
                status = json_text['status']
            else:
                status = ''



## Done. Now the logic: 
## 1. If there is a URL and that URL already exists in the csv, replace the values in the CSV  
## 2. If there is no CSV, then create a new entry with the values. 

## Also update the data table:
# the URL for the resource is a hyperlink on the resource name - opens a new window 
# the URL for the maintainer is a hyperlink on the owner - opens a new window 


 
# save the CSV back



print(df)
