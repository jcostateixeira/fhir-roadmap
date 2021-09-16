import os, json
import pandas as pd
import glob


def create_current_df(path):
    if os.path.exists(path):
        df = pd.read_csv(path, sep =';', header=0).to_dict(orient="records")
        return df
    else:
        return None

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
        print(js)
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
                        record["dtype"]="Logical Model"
                    if (json_text['type']=='extension'): # in this case, it's an  extension
                        record["dtype"]="Extension"
                    if (json_text['kind']=='resource'): # in this case, it's a profile
                        record["dtype"]="Profile"
                    if (json_text['kind']=='complex-type') and (json_text['type']!='extension'): # in this case, it's a data type
                        record["dtype"]="Data type"
                else:
                    record["dtype"]=rtype # for other resources, the resource type is the detailed ty
                    record["name"] = json_text.get('name')
                    record["version"] = json_text.get('version')
                    record["url"] = json_text.get('url')
                    record["date"] = json_text.get('date')

                    record["status"] = json_text.get('status')

                #print(record)
                print(result)
                print("NEWWW---------------------------------")
                result.append(record)
    print(result)
    return result


## Done. Now the logic: 
## 1. If there is a URL and that URL already exists in the csv, replace the values in the CSV  
## 2. If there is no CSV, then create a new entry with the values. 

## Also update the data table:
# the URL for the resource is a hyperlink on the resource name - opens a new window 
# the URL for the maintainer is a hyperlink on the owner - opens a new window 


 
# save the CSV back

#df=create_current_df('resources.csv')

#print(df)

n_list= read_package("packages/")
#print(n_list)

n_df=pd.DataFrame(n_list)
n_df.to_csv("resources.csv")