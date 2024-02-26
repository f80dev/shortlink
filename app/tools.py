
import base64
import datetime
import json
import os
import random
from base64 import b64encode

from pymongo import MongoClient

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
  for c in cache:
    if c[field]==value: cache.remove(c)

  stats["write"]+=1
  rc=db["links"].delete_one({field:value})
  return rc.deleted_count==1




def get_url(cid:str) -> str:
  data=find(cid,"cid")  #récupere la donnée associée au cid

  #Condition d'éligibilité
  if is_expired(data): return ""
  if data is None: return f"{cid} inconnu"

  if data["service"]!="":
    #On doit appliquer un service a l'url
    _service=db["services"].find_one({"service":data["service"]})
    url=_service["url"].replace("{url}",str(base64.b64encode(bytes(data["url"],"utf8")),"utf8"))
  else:
    url=data["url"]

  if  type(url)==dict:
    #l'url récupérer est un dictionnaire il faut donc récupérer l'url de redirection dans le dictionnaire et créer le lien avec les autres parametres
    u=url[REDIRECT_NAME]
    del url[REDIRECT_NAME]
    url=u+"?p="+str(base64.b64encode(bytes(json.dumps(url),"utf8")),"utf8")

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


def del_service(service:str):

  rc=db["services"].delete_one({"service":service})
  return rc.deleted_count>0

def get_services():
  rc=list(db["services"].find())
  for service in rc:
    del service["_id"]
  rc.append({"service":"Redirection simple","url":"","dtCreate":0})
  return rc




def add_service(service:str,url:str):
  _service=db["services"].find_one({"service":service})
  if _service is None:
    stats["write"]+=1
    rc=db["services"].insert_one({"service":service,"url":url})
    return rc.acknowledged


def is_expired(data:dict) -> bool:
  now=int(datetime.datetime.now().timestamp())
  if data["duration"]>0 and data["dtCreate"]+data["duration"]<now: return True
  return False


def add_url(url:str or dict,service:str="",prefix="",duration=0) -> str:
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
    if len(service)>0 and db["services"].find_one({"service":service}) is None:
      raise RuntimeError(f"Service {service} inconnu")

    stats["write"]+=1
    now=int(datetime.datetime.now().timestamp())
    data={"cid":cid,"url":url,"service":service,"dtCreate":now,"duration":duration}
    db["links"].insert_one(data)

    cache.insert(0,data)
    if len(cache)>CACHE_SIZE: cache.remove(cache[CACHE_SIZE])       #La taille du cache se limite a CACHE_SIZE

  return prefix+cid
