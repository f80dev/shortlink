
import base64
import datetime
import os
import random
from base64 import b64encode

from pymongo import MongoClient

#valeurs possibles
#  - mongodb://root:hh4271@38.242.210.208:27017/?tls=false
#  - mongodb+srv://Hhoareau:hh4271@cluster0.mr2j9.mongodb.net/?retryWrites=true&w=majority

dbpath=os.environ["DBPATH"] if "DBPATH" in os.environ else "mongodb+srv://Hhoareau:hh4271@cluster0.mr2j9.mongodb.net/?retryWrites=true&w=majority"
dbname=os.environ["DBNAME"] if "DBNAME" in os.environ else "shortlinks"
db = MongoClient(dbpath)[dbname]
#db = MongoClient("mongodb://root:hh4271@38.242.210.208:27017/?tls=false")["shortlinks"]



def toBase64(n:int):
  nombre_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
  return b64encode(nombre_bytes).decode("ascii")


def find(cid:str,field="cid"):
  return db["links"].find_one({field:cid})


def _all(limit=2000):
  rc=[]
  for obj in db["links"].find().limit(limit):
    del obj["_id"]
    rc.append(dict(obj))
  return rc

def delete(cid:str,field="cid"):
  rc=db["links"].delete_one({field:cid})
  return rc.deleted_count==1




def get_url(cid:str) -> str:
  data=find(cid,"cid")

  #Condition d'éligibilité
  now=int(datetime.datetime.now().timestamp())
  if is_expired(data): return ""
  if data is None: return f"{cid} inconnu"


  if data["service"]!="":
    _service=db["services"].find_one({"service":data["service"]})
    url=_service["url"].replace("{url}",str(base64.b64encode(bytes(data["url"],"utf8")),"utf8"))
  else:
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


def del_service(service:str):
  rc=db["services"].delete_one({"service":service})
  return rc.deleted_count>0


def add_service(service:str,url:str):
  _service=db["services"].find_one({"service":service})
  if _service is None:
    rc=db["services"].insert_one({"service":service,"url":url})
    return rc.acknowledged


def is_expired(data:dict) -> bool:
  now=int(datetime.datetime.now().timestamp())
  if data["duration"]>0 and data["dtCreate"]+data["duration"]<now: return True
  return False


def add_url(url:str,service:str="",prefix="",duration=0) -> str:
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

    now=int(datetime.datetime.now().timestamp())
    data={"cid":cid,"url":url,"service":service,"dtCreate":now,"duration":duration}
    db["links"].insert_one(data)

  return prefix+cid
