
import base64
import datetime
import hashlib
import json
import os
import random
from base64 import b64encode

import yaml
from pymongo import MongoClient

from secret import TRANSFER_APP

CACHE_SIZE=1000

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
  for c in cache:
    if c[field]==value: cache.remove(c)

  stats["write"]+=1
  rc=db["links"].delete_one({field:value})
  return rc.deleted_count==1




def get_url(cid:str,format=None) -> str:
  data=find(cid,"cid")

  #Condition d'éligibilité
  if is_expired(data): return ""
  if data is None: return f"{cid} inconnu"

  if data["service"]!="":
    _service=db["services"].find_one({"service":data["service"]})
    url=_service["url"].replace("{url}",str(base64.b64encode(bytes(data["url"],"utf8")),"utf8"))
  else:
    url=data["url"]

  if format=="url" and type(url)==dict:
    u=data["url"]
    for k in url.keys():
      u=u+k+"="+url[k]
    url=u

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
  with open(service_file,"r") as hFile:
    for service in yaml.load(hFile,yaml.FullLoader)["services"]:
      service["url"]=service["url"].replace("{{redirect_server}}",TRANSFER_APP)
      if not db["services"].find_one({"id":service["id"]}):
        db["services"].insert_one(service)


def get_services():
  rc=list(db["services"].find())
  for service in rc:
    del service["_id"]

  return rc




def add_service(service:str,url_or_dict:str or dict,id="",description=""):
  if id=="":
    url=url_or_dict if type(url_or_dict)==str else json.dumps(url_or_dict)
    id=hashlib.sha256(bytes(url,'utf8')).hexdigest()

  _service=db["services"].find_one({"id":id})

  if _service is None:
    stats["write"]+=1
    body={"service":service,"url":url_or_dict,"id":id,"desc":description}
    rc=db["services"].insert_one(body)
    if rc.acknowledged: return body

  return None     #En cas d'échec


def is_expired(data:dict) -> bool:
  now=int(datetime.datetime.now().timestamp())
  if data["duration"]>0 and data["dtCreate"]+data["duration"]<now: return True
  return False


def add_url(url:str,service_id:str="",prefix="",duration=0) -> str:
  """

  :param url:
  :return:
  """
  cid=None
  obj=find(url,"url")
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
    data={"cid":cid,"url":url,"service":service_id,"dtCreate":now,"duration":duration}
    db["links"].insert_one(data)

    cache.insert(0,data)
    if len(cache)>CACHE_SIZE: cache.remove(cache[CACHE_SIZE])       #La taille du cache se limite a CACHE_SIZE

  return prefix+cid
