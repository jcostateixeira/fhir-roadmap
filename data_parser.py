import json
import pandas as pd


nodes_list=[]
edges_list=[]
final_data={"data":[]}

def create_edges(element,relation_list,relationship_type_list,sep="|"):
    edge_info={"transaction":("transaction","Transaction From","bar","#7a8989"),"questionnaire":("questionnaire","Questionnnaire From","bar","#453C5E"),"namingsystem":("system","System","diamond", "#404040" ),"codesystem":("values_from","Values from","arrow", "#404000" ),"valueset":("binding_req","Bound (Req)","arrow", "#000000"),"extension":("extension","Extension","curve", "#400000" ),"logicalmodel":("logical_model_from","Model from","arrow", "#000000"),"system":("system","System","diamond", "#404040" )}

    if len(relation_list)==0:
        return None
    relation=relation_list.split(sep)

    for node in relation:
        r=edge_info[element["type"].lower()][0]
        r_label=edge_info[element["type"].lower()][1]
        arrows=edge_info[element["type"].lower()][2]
        arrow_color=edge_info[element["type"].lower()][3]
        edge={"from": node,"to": element["id"], "relation":r, "label": r_label,"arrows": {"to":{ "enabled": True,"type":arrows} },"color": { "color": arrow_color }}
        edges_list.append(edge)


def get_data_and_create_node(datafile="resources.csv"):
    data=pd.read_csv(datafile,encoding="iso8859_1",sep=";",keep_default_na=False)

    colors={"Transaction":"#cce5e5","Questionnaire":"#AD97EC","ImplementationGuide":"#AABBCC","DataType":"#83986B","Profile":"#CFCFCF","CodeSystem":"#CFFFFF","ValueSet":"#CFFFCF","Extension":"#FFCFCF","NamingSystem":"#FFCFFF","LogicalModel":"#87BEEF","Data type":"#CEBECF"}

    for idx,element in data.iterrows():
    #  if element["topic"]=="Vaccination": #test only
            res={}



        #  print(element["topic"])
            res["id"]=element["id"]

            res["topic"]=element["topic"]
            res["subtopic"]=element["subtopic"]
            res["name"]=element["name"]
            res["type"]=element["type"]
            res["status"]=element["status"]
            res["size"]=170
            res["shape"]="box"
            res["font"]={ "align": "left", "multi":"md" }
            res["color"]=colors[element["type"]]

            res["date_started"]=element["date_started"]
            res["date_published"]=element["date_published"]
            res["date_reviewed"]=element["date_reviewed"]
            res["maturity"]=element["maturity"]
            res["legal"]=element["legal"]
            res["version"]=element["version"]


# relation;
# relation_type;
# date;
# owner;
# pack_author;
# pack_last_review_date;
# pack_wg_url




            if element["status"]=="":
                status="draft"
            else:
                status=element["status"]
            res["label"]="*"+element["name"]+"**\n("+element["type"]+")\nStatus: "+status
            create_edges(element,element["relation"],element["relation_type"])
            nodes_list.append(res)


    with open("data/nodes.json", "w") as fout:
        json.dump(nodes_list, fout)

    with open("data/edges.json", "w") as fout:
        json.dump(edges_list, fout)

    final_data["data"]=data.to_dict(orient="records")
    with open("data/data.json", "w") as fout:
        json.dump(final_data, fout)

get_data_and_create_node()

