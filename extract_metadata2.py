import os, json
import pandas as pd
import glob
from csv_diff import load_csv, compare
import datetime


EXCLUSION_LIST=['package-list.json',".index.json",'package.json',"validation-summary","example"]

def create_current_df(path):
    """
    reads a csv in the specified folder, if it does not exists returns None
    """
    if os.path.exists(path):
        df = pd.read_csv(path,sep=";", header=0)
        return df
    else:
        return None


def get_target_id(row,resources_df):
    for idx,r in resources_df.iterrows():
     #   print(idx,r)
     #   print(row["target_url"])
        if row["target_url"]==r["url"]:
            return r["id"]
    return None

def extract_relation(res,resource_type):
    """
    this function takes a unique resource and create the entries for relation.csv
    Logic:
    Profile:
        Bound (Req) = element.binding[strength = required].valueset
        Bound (Ext) = element.binding[strength = extensible].valueset
        Bound (Pref) = element.binding[strength = preferred].valueset
        Bound (Exam) = element.binding[strength = example].valueset
        Extension = element.type[code = extension].profile

    ValueSet:
        valuesFrom = compose.include.system
        valuesFrom = expansion.contains.system
        includes = compose.include.valueSet
    """
    dict_relat=[]
    relation_type_data={"required":"Bound_Req","extensible":"Bound_Ext","preferred":"Bound_Pref","example":"Bound_Exam"}
   # if res.get("id")=="be-ext-laterality":
   #     print(resource_type,res.get("id"))
    if resource_type in ["Profile","Data type"]:
        elements=res.get('snapshot', {}).get('element',[] )
        for element in  elements:
            binding=element.get("binding",{}).get("strength") 
            value=element.get("binding",{}).get("valueSet")
            if binding:
              #  print(value)
                stripped = value.split("|", 1)[0] #remove pipes
             #   if res.get("id")=="be-allergyintolerance":
            #      print(stripped)
                #print(resource_type,"binding -> ",binding,value)
                dict_relat.append({"source":res.get("id"),"target_url":stripped,"relation":relation_type_data[binding]})
            for l in element.get("type",[]):
                if l.get("code",{})=="Extension":
                    #pass
                    if l.get("profile"):
                        dict_relat.append({"source":res.get("id"),"target_url":l.get("profile")[0],"relation":"extension"})
                for target_profile in l.get("targetProfile",[]):
                    dict_relat.append({"source":res.get("id"),"target_url":target_profile,"relation":"references"})

                 #   print()

        elements=res.get('differential', {}).get('element', [])

        for element in  elements:
            binding=element.get("binding",{}).get("strength") 
            value=element.get("binding",{}).get("valueSet")
            if binding:
               # print(res.get("id"),value)
              #  print(value,res.get("id"))
                stripped = value.split("|", 1)[0] #remove pipes

                #print(resource_type,"binding -> ",binding,value)
                dict_relat.append({"source":res.get("id"),"target_url":stripped,"relation":relation_type_data[binding]})
            for l in element.get("type",[]):
                if l.get("code",{})=="Extension":
                    #pass
                    if l.get("profile"):
                    #    print(l.get("profile")[0],res.get("id"))
                        dict_relat.append({"source":res.get("id"),"target_url":l.get("profile")[0],"relation":"extension"})
                for target_profile in l.get("targetProfile",[]):
                    dict_relat.append({"source":res.get("id"),"target_url":target_profile,"relation":"references"})

                 #   print()
    elif resource_type=="ValueSet":
        for s in res.get("compose",{}).get("include",[]):
            #print(s)
            if s.get("system"):
                dict_relat.append({"source":res.get("id"),"target_url":s.get("system"),"relation":"valuesFrom"})
            if s.get("valueSet"):
              #  print(s.get("valueSet"))
                dict_relat.append({"source":res.get("id"),"target_url":s.get("valueSet")[0],"relation":"includes"})

        #print(res.get("expansion",{}).get("contains",[]))

    return dict_relat

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
    relations=[]
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
        if  not any(ext in js for ext in EXCLUSION_LIST):   # for all other jsons:
            with open(js, encoding='utf-8') as json_file:
                record=record_upper.copy()
                json_text = json.load(json_file)

                # get the rtype (resource type) and dtype (actual detailed type)
                rtype = json_text['resourceType']
                record["id"]= json_text.get('id')
                if (rtype=="StructureDefinition"):
                    if (json_text['kind']=='logical'): # in this case, this is a logical model
                        record["type"]="Logical Model"
                    if (json_text['type']=='extension'): # in this case, it's an  extension
                        record["type"]="Extension"
                    if (json_text['kind']=='resource'): # in this case, it's a profile
                        record["type"]="Profile"
                    if (json_text['kind']=='complex-type') and (json_text['type']!='extension'): # in this case, it's a data type
                        record["type"]="Data type"
                else:
                    record["type"]=rtype # for other resources, the resource type is the detailed ty


                if (rtype=="NamingSystem"):
                    if ("uniqueId" in json_text) :
                       uris = [x for x in json_text["uniqueId"] if (x["type"] == "uri" )] 
                       record["url"] = [x for x in uris if x["preferred"] == True][0]["value"]
                else:
                    record["url"] = json_text.get('url')

#                record["type"] = record["dtype"]
#                record.pop("dtype")


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
               # record["relation"] = json_text.get('relation')
               # record["relation_type"] = json_text.get('relation_type')
                record["legal"] = json_text.get('legal')
                relations.extend(extract_relation(json_text,record["type"])) #adds entries to relation list
                result.append(record)
  #  print(result)
  #  print(relations)
    #relation_unique = {x['source']:x for x in relations}.values() #dont quite know why so much duplicates
    #df_relation=pd.DataFrame(relation_unique)#.drop_duplicates()
   # try:
    df_relation=pd.DataFrame(relations).drop_duplicates()
   # except:
       # pd.DataFrame(relations).to_csv("erro.csv")
       # break
  #  print(df_relation)
    # we cannot assume csv exists when creating, so after each package folder we search for it in the elements
    df_relation["target_id"]=df_relation.apply(get_target_id,resources_df=pd.DataFrame(result),axis=1)
  # print(df_relation.head(10))
    return pd.DataFrame(result),df_relation


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


def update_resource_csv(old,new):
    #all columns here are overlaped by procedure, for other sutff, remove or change
    list_of_changes={"updated":[],"created":[],"other":[]}
    for idx,row in new.iterrows(): #for every row in new df
        #print(row["url"])
        if row["url"] in old["url"].values: #if url in new df is in old df
            #update values
            list_of_changes["updated"].append(row["url"])
            old.loc[old["url"]==row["url"],"date"]=row.get("date")
            old.loc[old["url"]==row["url"],"version"]=row.get("version")
            old.loc[old["url"]==row["url"],"status"]=row.get("status")
            old.loc[old["url"]==row["url"],"type"]=row.get("type")
            old.loc[old["url"]==row["url"],"id"]=row.get("id")
            old.loc[old["url"]==row["url"],"pack_wg_url"]=row.get("pack_wg_url")
            old.loc[old["url"]==row["url"],"pack_author"]=row.get("pack_author")
            old.loc[old["url"]==row["url"],"pack_last_review_date"]=row.get("pack_last_review_date")

            old.loc[old["url"]==row["url"],"date_started"]=row.get("date_started")
            old.loc[old["url"]==row["url"],"date_published"]=row.get("date_published")
            old.loc[old["url"]==row["url"],"date_reviewed"]=row.get("date_reviewed")
            old.loc[old["url"]==row["url"],"maturity"]=row.get("maturity")
            old.loc[old["url"]==row["url"],"legal"]=row.get("legal")
            

        elif row["url"] is not None: #if does not exist, add to df (must have url)
            #print(row)
            list_of_changes["created"].append(row["url"])
            old=old.append(row,ignore_index=True)
        else:
            list_of_changes["other"].append("something weird on row "+str(idx))

    #save the old again
    old.to_csv("resources.csv",sep=";",index=False)
    #return track changes

    return list_of_changes

def update_relation_csv(old,new):
    #print(new.head(10))
   # print(old,new)
    ###right now it overlaps manual actions
    list_of_changes={"updated":[],"created":[],"other":[]}
    #make primary key on both df:
    old["pk"]=old["source"]+old["target_url"]
    #try:
    new["pk"]=new["source"]+new["target_url"]
   # except Exception as err:
      #  print("eerorrrr------------",err)
       # print(new)
      #  new.to_csv("errro.csv")
    for idx,row in new.iterrows(): #for every row in new df
        #print(row["url"])
        if row["pk"] in old["pk"].values: #if primary key exists (source+target)
        
            #update values
            list_of_changes["updated"].append(row["source"])
            old.loc[old["pk"]==row["pk"],"target_id"]=row.get("target_id")
            old.loc[old["pk"]==row["pk"],"relation"]=row.get("relation")
            old.loc[old["pk"]==row["pk"],"target_url"]=row.get("target_url")

        elif row["source"] is not None: #if does not exist, add to df (must have url)
            #print(row)
            list_of_changes["created"].append(row["source"])
            old=old.append(row,ignore_index=True)
        else:
            list_of_changes["other"].append("something weird on row "+str(idx)) 

    #save the old again
    old.drop(columns=["pk"],inplace=True)
    old.to_csv("relation.csv",sep=";",index=False)
    #return track changes

    return list_of_changes


def create_csv_and_update(current_resource,current_relation,package_folder):
## Done. Now the logic: 
## 1. If there is a URL and that URL already exists in the csv, replace the values in the CSV  
## 2. If there is no CSV, then create a new entry with the values. 

## Also update the data table:
# the URL for the resource is a hyperlink on the resource name - opens a new window 
# the URL for the maintainer is a hyperlink on the owner - opens a new window 
# url is the 
  #  print(current_resource)
    outcome={"resource_status":"error","resource_outcome":"N/A","relation_outcome":"N/A","relation_status":"error"}
    resource_df,relation_df=read_package(package_folder)
    #print(relation_df)
  #  print(n_relation)
   # n_df.to_csv("new_.csv",sep=";",index=False)
    if type(current_resource)==pd.DataFrame and len(resource_df)>0:
        print("has a resource csv which was updated")
        changes=update_resource_csv(current_resource,resource_df)
        #return changes
        outcome["resource_status"]="changed"
        outcome["resource_outcome"]=changes
    elif type(current_resource)!=pd.DataFrame and len(resource_df)>0:
        print("no resource csv and new written")
        resource_df.to_csv("resources.csv",sep=";",index=False)
        #return None
        outcome["resource_status"]="new"

    else:
        print("no resource csv and not able to create new")

    if type(current_relation)==pd.DataFrame and len(relation_df)>0:
        print("has a relation csv which was updated")
        changes=update_relation_csv(current_relation,relation_df)
        #return changes
        outcome["relation_status"]="changed"
        outcome["relation_outcome"]=changes
    elif type(current_relation)!=pd.DataFrame and len(relation_df)>0:
        print("no relation csv and new written")
        relation_df.to_csv("relation.csv",sep=";",index=False)
        #return None
        outcome["relation_status"]="new"

    else:
        print("no relation csv and not able to create new")

    return outcome


def getPackageFolders(path):
    directoryList = []

    #return nothing if path is a file
    if os.path.isfile(path):
        return []

    #add dir to directorylist if it contains package.json files
    if len([f for f in os.listdir(path) if (f == 'package.json')])>0:
        with open(path+"/package.json") as packge_file:
            pkg_json=json.load(packge_file)
         #   print(pkg_json)
            package_date=pkg_json.get("date") #not all have date
            if not package_date:
               raise ValueError("Package without date: "+path)
              # package_date="19900801000000" just for testing
            directoryList.append((path,datetime.datetime.strptime(package_date, '%Y%m%d%H%M%S')))
    # here, check the package.json and populate the list with the directory and the date in the json
    for d in os.listdir(path):
        new_path = os.path.join(path, d)
        if os.path.isdir(new_path):
            directoryList.extend(getPackageFolders(new_path)) 
    # now, sort the directotyList by the date
  #  print(directoryList)
   #
    return sorted(directoryList, key=lambda tup:(tup[1], tup[0]))


def main(package_folder):
    folders = getPackageFolders(package_folder)
    print("Folders---",folders)

    current_df=create_current_df("resources.csv")
    current_relation=create_current_df("relation.csv")
    if type(current_df)==pd.DataFrame:
        current_df.to_csv("resources_backup.csv",sep=";",index=False)
    if type(current_relation)==pd.DataFrame:
        current_relation.to_csv("relation_backup.csv",sep=";",index=False)

    for pack in folders:
        current_df=create_current_df("resources.csv")#redo for newly created data in loop
        current_relation=create_current_df("relation.csv")#redo for newly created data in loop
        create_csv_and_update(current_df,current_relation,pack[0])

    if  os.path.exists("resources_backup.csv"):
        
        diff = compare(
            load_csv(open("resources_backup.csv"), key="url"),
            load_csv(open("resources.csv"), key="url")
        )
        print(diff)

        diff_df=pd.DataFrame.from_dict(diff,orient='index').T
        diff_df["timestamp"]=datetime.datetime.now().strftime("%Y%m%d%H")
        #check if diff exists:
        if not os.path.exists("diff.csv"):
            diff_df.to_csv("diff.csv",sep=";",index=False)
        else:
            current_diff=create_current_df("diff.csv")
            current_diff.append(diff_df,ignore_index=True)
            current_diff.to_csv("diff.csv",sep=";",index=False)
    return "ok"
main("packages")

#print(dict_relat)