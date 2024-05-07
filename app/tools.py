
import base64
import datetime
import hashlib
import json
import logging
import os
import random
from base64 import b64encode
from urllib import parse

import requests
import yaml
from pymongo import MongoClient

from secret import TRANSFER_APP, DBPATH

CACHE_SIZE=1000
REDIRECT_NAME="url"

#valeurs possibles
#  - mongodb://root:hh4271@38.242.210.208:27017/?tls=false
#  - mongodb+srv://Hhoareau:hh4271@cluster0.mr2j9.mongodb.net/?retryWrites=true&w=majority
# mongodb+srv://hhoareau:hh4271@cluster0.fsd0zro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

logging.basicConfig(level=logging.INFO)

key=os.environ["DBPATH"] if "DBPATH" in os.environ else "cloud"
dbpath=DBPATH[key] if key in DBPATH else key
dbname=os.environ["DBNAME"] if "DBNAME" in os.environ else "shortlinks"
db = MongoClient(dbpath)[dbname]


logging.info(f"Connexion à la base {dbname} sur {dbpath}")

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

def del_link(value:str, field="cid"):
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
  """
  Transform a dict to url and use key domain for the domain
  :param obj:
  :param key_domain:
  :param convert_mode:
  :return:
  """

  obj=obj.copy()
  domain=""
  if len(key_domain)>0:
    domain=obj[key_domain]
    del obj[key_domain]

  if convert_mode=="base64":
    params=["b="+parse.quote(str(base64.b64encode(bytes(json.dumps(obj),"utf8")),"utf8"))]
  else:
    params=[k+"="+parse.quote(str(obj[k]), safe="/",encoding=None, errors=None) for k in obj.keys()]
  rc=domain+("?" if len(params)>0 else "")+"&".join(params)
  return rc



def get_url(cid:str) -> str:
  cid=str(cid)
  data=find(cid,"cid")

  #Condition d'éligibilité
  if data is None:
    logging.error(f"{cid} inconnu")
    return None

  if is_expired(data):
    return None

  if not "values" in data:data["values"]=dict()
  data["values"]["url"]=data["url"]
  url=data["url"]

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



def init_services(service_file="./static/services.yaml",replace=False):
  """
  Chargement des services disponibles en plus du raccourcissement simple
  http://localhost/api/init_services
  :param service_file:
  :param replace:
  :return:
  """
  logging.info(f"Chargement des services depuis {service_file}")

  hFile=None
  if service_file.startswith("http"):
    resp=requests.get(service_file)
    if resp.status_code==200:
      hFile=resp.content
    else:
      logging.error("Impossible de charger le fichier indiqué")
      service_file="./static/services.yaml"

  if hFile is None:
    hFile=open(service_file,"r",encoding="utf8")

  services=yaml.safe_load(hFile)["services"]
  for service in services:
    if replace:
      logging.info("Remplacement de "+service["id"]+" par "+json.dumps(service))
      if db["services"].delete_one({"id":service["id"]}).deleted_count==0:
        logging.warning("Impossible de supprimer "+service["id"])

    if not db["services"].find_one({"id":service["id"]}):
      if not "params" in service:service["params"]=dict()
      add_service(service)


def get_services():
  rc=list(db["services"].find())
  for service in rc:
    del service["_id"]

  return rc

def get_links():
  rc=list(db["links"].find())
  for link in rc:
    del link["_id"]

  return rc




def add_service(service:dict):
  logging.info("Ajout du service "+str(service))
  #if not "domain" in data: raise RuntimeError("Le service doit contenir un domain")

  if "id" not in service:
    id=hashlib.sha256(bytes(json.dumps(service),'utf8')).hexdigest()

  _service=db["services"].find_one({"id":service["id"]})

  if _service is None:
    stats["write"]+=1
    rc=db["services"].insert_one(service)
    if rc.acknowledged: return service

  return None     #En cas d'échec


def is_expired(data:dict) -> bool:
  delay=datetime.datetime.now().timestamp()-data["dtCreate"]

  if data["duration"]>0 and delay>data["duration"]: return True
  return False


def add_url(url:str or dict,values:dict=dict(),prefix="",duration=0) -> str:
  """

  :param url:
  :return:
  """
  #if service_id=="": service_id=get_services()[0]["id"]
  if type(url)==dict: url=convert_dict_to_url(url,"url")
  cid=None


  # _service=db["services"].find_one({"id":service_id})
  # if _service is None:
  #   raise RuntimeError(f"Service {service_id} inconnu")

  #_service["data"]["service"]=service_id
  if values!=dict():
    url=url+convert_dict_to_url(values,"")
  # if _service["params"]!=dict():
  #   _data=appply_values_on_service(_service["params"],values)


  obj=db["links"].find_one({"url":url})
  if obj:
    if is_expired(obj):
      del_link(url, "url")
    else:
      cid=obj["cid"]

  if cid is None:
    cid=generate_cid()
    if cid=="": raise RuntimeError("impossible de généré le CID")

    stats["write"]+=1
    now=int(datetime.datetime.now().timestamp())

    data={"cid":cid,"url":url,"dtCreate":now,"duration":duration}
    db["links"].insert_one(data)
    cache.insert(0,data)
    if len(cache)>CACHE_SIZE: cache.remove(cache[CACHE_SIZE])       #La taille du cache se limite a CACHE_SIZE

  return prefix+cid
