import os, json
import pandas as pd
import glob


def create_current_df(path):
    """
    reads a csv in the specified folder, if it does not exists returns None
    """
    if os.path.exists(path):
        df = pd.read_csv(path,sep=";", header=0)
        return df
    else:
        return None


def read_package(folder):
    """
    reads a folder and every json inside it and subsequent folders.
    From them, the keys are extracted and a df is built
    """
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
      #  print(js)
        if  not any(ext in js for ext in ['package-list.json',".index.json",'package.json',"validation-summary","example"]):   # for all other jsons:
            with open(js, encoding='utf-8') as json_file:
                record=record_upper.copy()
                json_text = json.load(json_file)

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
              
                if (rtype=="NamingSystem"):
                    if ("uniqueId" in json_text) :
                       uris = [x for x in json_text["uniqueId"] if (x["type"] == "uri" )] 
                       record["url"] = [x for x in uris if x["preferred"] == True][0]["value"]
                else:
                    record["url"] = json_text.get('url')

                # check if the paths are correct
                record["name"] = json_text.get('name')
                record["version"] = json_text.get('version')
                record["date"] = json_text.get('date')
                record["topic"] = json_text.get('topic')
                record["subtopic"] = json_text.get('subtopic')
                record["owner"] = json_text.get('owner')
                record["maturity"] = json_text.get('maturity')
                record["status"] = json_text.get('status')
                record["pack_wg_url"] = json_text.get('pack_wg_url')
                record["pack_author"] = json_text.get('pack_author')
                record["pack_last_review_date"] = json_text.get('pack_last_review_date')
                record["relation"] = json_text.get('relation')
                record["relation_type"] = json_text.get('relation_type')
                record["legal"] = json_text.get('legal')

                result.append(record)
  #  print(result)
    return pd.DataFrame(result)


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


def update_csv(old,new):

    for idx,row in new.iterrows(): #for every row in new df
        #print(row["url"])
        if row["url"] in old["url"].values: #if url in new df is in old df
            #update values
            old.loc[old["url"]==row["url"],"date"]=row["date"]
            old.loc[old["url"]==row["url"],"version"]=row["version"]
            old.loc[old["url"]==row["url"],"status"]=row["status"]
            old.loc[old["url"]==row["url"],"dtype"]=row["dtype"]
            old.loc[old["url"]==row["url"],"id"]=row["id"]
            old.loc[old["url"]==row["url"],"pack_wg_url"]=row["pack_wg_url"]
            old.loc[old["url"]==row["url"],"pack_author"]=row["pack_author"]
            old.loc[old["url"]==row["url"],"pack_last_review_date"]=row["pack_last_review_date"]
            old.loc[old["url"]==row["url"],"relation"]=row["relation"]
            old.loc[old["url"]==row["url"],"relation_type"]=row["relation_type"]
        else: #if does not exist, add to df
            #print(row)
            old=old.append(row,ignore_index=True)
    #save the old again
    old.to_csv("resources.csv",sep=";",index=False)

def create_csv_and_update(csv_path,package_folder):
## Done. Now the logic: 
## 1. If there is a URL and that URL already exists in the csv, replace the values in the CSV  
## 2. If there is no CSV, then create a new entry with the values. 

## Also update the data table:
# the URL for the resource is a hyperlink on the resource name - opens a new window 
# the URL for the maintainer is a hyperlink on the owner - opens a new window 
# url is the 
    current_df=create_current_df(csv_path)
  #  print(current_df)
    if type(current_df)==pd.DataFrame:
        current_df.to_csv("current_backup.csv",sep=";",index=False)
    n_df=read_package(package_folder)
   # n_df.to_csv("new_.csv",sep=";",index=False)
    if type(current_df)==pd.DataFrame:
        print("has a csv")
        update_csv(current_df,n_df)
    else:
        n_df.to_csv("resources.csv",sep=";",index=False)

    

create_csv_and_update("resources.csv","packages")