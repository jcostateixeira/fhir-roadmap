import json
import pandas as pd


nodes_list=[]
edges_list=[]
final_data={"data":[]}

def create_edges(element,relationdf):
    """
    binding_req: true,
    binding_req: true,
    binding_ext: true,
    binding_pref: true,
    binding_exm: true,
    extension: true,
    contains: true,
    values_from: true,
    system: true,
    logical_model_from: true,
    transaction: true,
    questionnaire: true,
    includes: true
    """
    #edge_info={"profile":("","","",""),"transaction":("transaction","Transaction From","bar","#7a8989"),"questionnaire":("questionnaire","Questionnnaire From","bar","#453C5E"),"namingsystem":("system","System","diamond", "#404040" ),"codesystem":("values_from","Values from","arrow", "#404000" ),"valueset":("binding_req","Bound (Req)","arrow", "#000000"),"extension":("extension","Extension","curve", "#400000" ),"logicalmodel":("logical_model_from","Model from","arrow", "#000000"),"system":("system","System","diamond", "#404040" )}
    new_edge_info={"references":("references","references","curve","#000000"),"includes":("includes","Includes","bar","#7a8989"),"valuesFrom":("values_from","Values from","arrow", "#404000" ),"Bound_Exam":("binding_exm","Bound (Exam)","arrow", "#000000"),"Bound_Pref":("binding_pref","Bound (Pref)","arrow", "#000000"),"Bound_Ext":("binding_ext","Bound (Ext)","arrow", "#000000"),"Bound_Req":("binding_req","Bound (Req)","arrow", "#000000"),"extension":("extension","Extension","curve", "#400000" )}
    #print(element["id"])

    relation_list=relationdf[relationdf["source"]==element["id"]]
    #print(relation_list)
    if len(relation_list)==0:
        return None
    #else:
       # print(relation_list)
    #relation=relation_list.split(sep)

    for idx,node in relation_list.iterrows():
        if node["source"] and node["target_id"]:
            print(node["relation"])
            r=new_edge_info[node["relation"]][0]
            r_label=new_edge_info[node["relation"]][1]
           # r_label=node["relation"]
            arrows=new_edge_info[node["relation"]][2]
            arrow_color=new_edge_info[node["relation"]][3]
            edge={"from": node["target_id"],"to": element["id"], "relation":r, "label": r_label,"arrows": {"to":{ "enabled": True,"type":arrows} },"color": { "color": arrow_color }}
         #   print(edge)
            edges_list.append(edge)


def get_data_and_create_node(datafile="data.csv",relationfile="relation.csv"):
    data=pd.read_csv(datafile,encoding="iso8859_1",sep=";",keep_default_na=False)
    relation=pd.read_csv(relationfile,encoding="iso8859_1",sep=";",keep_default_na=False)

    colors={"ImplementationGuide":"#a8b94b","Transaction":"#cce5e5","Questionnaire":"#AD97EC","DataType":"#83986B","Profile":"#CFCFCF","CodeSystem":"#CFFFFF","ValueSet":"#CFFFCF","Extension":"#FFCFCF","NamingSystem":"#FFCFFF","LogicalModel":"#87BEEF","Data type":"#CEBECF"}

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
            if element["status"]=="":
                status="draft"
            else:
                status=element["status"]
            res["label"]="*"+element["name"]+"**\n("+element["type"]+")\nStatus: "+status
            create_edges(element,relation)
            nodes_list.append(res)


    with open("data/nodes.json", "w") as fout:
        json.dump(nodes_list, fout)

    with open("data/edges.json", "w") as fout:
        json.dump(edges_list, fout)

    final_data["data"]=data.to_dict(orient="records")
    with open("data/data.json", "w") as fout:
        json.dump(final_data, fout)

get_data_and_create_node("resources.csv")

