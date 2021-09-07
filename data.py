import json

final_list=[]
# Opening JSON file
f = open('data/data.json',encoding="utf-8")
  
# returns JSON object as 
# a dictionary
data = json.load(f)
colors={"Transaction":"#008080","Questionnaire":"#AD97EC","DataType":"#83986B","Profile":"#CFCFCF","CodeSystem":"#CFFFFF","ValueSet":"#CFFFCF","Extension":"#FFCFCF","NamingSystem":"#FFCFFF","LogicalModel":"#87BEEF"}

for element in data["data"]:
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
    res["label"]="**"+element["name"]+"**\nStatus"+element["status"]
    final_list.append(res)


f = open("data/nodes2.json", "w")
f.write("[")
for element in final_list:
    f.write(json.dumps(element).replace("\\u00a0"," ") + ",\n")
f.write("]")
f.close()