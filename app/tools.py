
import base64
import datetime
import hashlib
import json
import logging
import os
import random
from base64 import b64encode
from urllib import parse

import yaml
from pymongo import MongoClient

from secret import TRANSFER_APP

CACHE_SIZE=1000
REDIRECT_NAME="url"

#valeurs possibles
#  - mongodb://root:hh4271@38.242.210.208:27017/?tls=false
#  - mongodb+srv://Hhoareau:hh4271@cluster0.mr2j9.mongodb.net/?retryWrites=true&w=majority

dbpath=os.environ["DBPATH"] if "DBPATH" in os.environ else "mongodb+srv://Hhoareau:hh4271@cluster0.mr2j9.mongodb.net/?retryWrites=true&w=majority"
dbname=os.environ["DBNAME"] if "DBNAME" in os.environ else "shortlinks"
db = MongoClient(dbpath)[dbname]
#db = MongoClient("mongodb://root:hh4271@38.242.210.208:27017/?tls=false")["shortlinks"]

cache=list()
stats={"dtStart":datetime.datetime.now(),"read":0,"write":0}

def toBase64(n:int):
  nombre_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
  return b64encode(nombre_bytes).decode("ascii")


def find(value:str,field="cid"):
  for c in cache:
    if c[field]==value: return c

  stats["read"]+=1
  return db["links"].find_one({field:value})


def _all(limit=2000):
  rc=[]
  for obj in db["links"].find().limit(limit):
    del obj["_id"]
    rc.append(dict(obj))
  return rc

def delete(value:str,field="cid"):
  if value=="*":
    rc=db["links"].delete_many({})
    cache.clear()
    return True

  else:
    for c in cache:
      if c[field]==value: cache.remove(c)

    stats["write"]+=1
    rc=db["links"].delete_one({field:value})
    return rc.deleted_count==1




def appply_values_on_service(service:dict,values:dict):
  for k in values.keys():
    for j in service.keys():
      if type(service[j])==dict:
        service[j]=appply_values_on_service(service[j],values)
      if k==j:
        service[j]=values[k]
  return service


def convert_dict_to_url(obj:dict,key_domain=REDIRECT_NAME,convert_mode="base64") -> str:
  if not key_domain in obj:raise RuntimeError("Le champs "+key_domain+" n'est pas présent dans l'objet")

  obj=obj.copy()
  domain=obj[key_domain]
  del obj[key_domain]
  if convert_mode=="base64":
    params=["b="+parse.quote(str(base64.b64encode(bytes(json.dumps(obj),"utf8")),"utf8"))]
  else:
    params=[k+"="+parse.quote(str(obj[k]), safe="/",encoding=None, errors=None) for k in obj.keys()]
  rc=domain+("?" if len(params)>0 else "")+"&".join(params)
  return rc



def get_url(cid:str) -> str:
  data=find(cid,"cid")

  #Condition d'éligibilité
  if data is None:
    logging.ERROR(f"{cid} inconnu")
    return None

  if is_expired(data):
    return None

  if not "values" in data:data["values"]=dict()
  data["values"]["url"]=data["url"]

  if data["service"] and data["service"]!="":
    data["service"]=db["services"].find_one({"id":data["service"]})
    if data["service"] is None: raise RuntimeError(f"Service {data['service']} inexistant")
    data["service"]=appply_values_on_service(data["service"]["data"],data["values"] if "values" in data else {})
    url=convert_dict_to_url(data["service"],key_domain="domain")
  else:
    url=data["url"]

  if type(url)==dict:
    url=convert_dict_to_url(url)

  return url




def generate_cid(ntry=3000) -> str:
  """

  :param ntry:
  :return:
  """
  for _ in range(ntry):
    cid=toBase64(random.randint(1,9999999999))
    if not "/" in cid:
      if find(cid) is None: return cid

  return ""


def del_service(service_id:str):
  if service_id=="*":
    rc=db["services"].delete_many({})
  else:
    rc=db["services"].delete_one({"id":service_id})
  return rc.deleted_count>0



def init_services(service_file="./static/services.yaml"):
  del_service("*")
  with open(service_file,"r") as hFile:
    for service in yaml.load(hFile,yaml.FullLoader)["services"]:
      if not "domain" in service["data"]:service["data"]["domain"]=TRANSFER_APP
      if not db["services"].find_one({"id":service["id"]}):
        service["data"]["url"]=""
        add_service(service["service"],service["data"],service["id"],service["description"])


def get_services():
  rc=list(db["services"].find())
  for service in rc:
    del service["_id"]

  return rc




def add_service(service:str,data:dict,id="",description=""):
  if not "domain" in data: raise RuntimeError("Le service doit contenir un domain")

  if id=="":
    id=hashlib.sha256(bytes(json.dumps(data),'utf8')).hexdigest()

  _service=db["services"].find_one({"id":id})

  if _service is None:
    stats["write"]+=1
    body={"service":service,"data":data,"id":id,"desc":description}
    rc=db["services"].insert_one(body)
    if rc.acknowledged: return body

  return None     #En cas d'échec


def is_expired(data:dict) -> bool:
  now=int(datetime.datetime.now().timestamp())
  if data["duration"]>0 and data["dtCreate"]+data["duration"]<now: return True
  return False


def add_url(url:str,service_id:str="",values:dict=dict(),prefix="",duration=0) -> str:
  """

  :param url:
  :return:
  """
  cid=None
  obj=db["links"].find_one({"url":url,"service":service_id})
  if obj:
    if is_expired(obj):
      delete(url,"url")
    else:
      cid=obj["cid"]

  if cid is None:
    cid=generate_cid()
    if cid=="": raise RuntimeError("impossible de généré le CID")

  if obj is None:
    if len(service_id)>0 and db["services"].find_one({"id":service_id}) is None:
      raise RuntimeError(f"Service {service_id} inconnu")

    stats["write"]+=1
    now=int(datetime.datetime.now().timestamp())
    data={"cid":cid,"url":url,"service":service_id,"dtCreate":now,"duration":duration,"values":values}
    db["links"].insert_one(data)

    cache.insert(0,data)
    if len(cache)>CACHE_SIZE: cache.remove(cache[CACHE_SIZE])       #La taille du cache se limite a CACHE_SIZE

  return prefix+cid
