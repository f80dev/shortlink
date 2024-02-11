import base64
import random
from base64 import b64encode

from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient

from secret import DBPATH

app = Flask(__name__)

db = MongoClient(DBPATH)["shortlinks"]

def toBase64(n:int):
  nombre_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
  return b64encode(nombre_bytes).decode("ascii")


def find(cid:str,field="cid"):
  return db["links"].find_one({field:cid})


def delete(cid:str,field="cid"):
  rc=db["links"].delete_one({field:cid})
  return rc.deleted_count==1


def get_url(cid:str) -> str:
  data=find(cid,"cid")
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



def add_url(url:str,service:str="") -> str:
  """

  :param url:
  :return:
  """
  obj=find(url,"url")
  if obj:
    cid=obj["cid"]
  else:
    cid=generate_cid()
    if cid=="": raise RuntimeError("impossible de généré le CID")

  if obj is None:
    if len(service)>0 and db["services"].find_one({"service":service}) is None:
      raise RuntimeError(f"Service {service} inconnu")

    data={"cid":cid,"url":url,"service":service}
    db["links"].insert_one(data)

  return cid



@app.route("/api/<cid>", methods=["GET"])
@app.route("/api", methods=["POST"])
def data(cid=""):
  if request.method == "GET":
    url=get_url(cid)
    format=request.args.get("format","redirect")
    if format=="json":
      return jsonify({"url":url} if len(url)>0 else {"Error":f"{cid} introuvable"})

    return redirect(url)

  elif request.method == "POST":
    service=request.json["service"] if "service" in request.json else ""
    data=add_url(request.json["url"],service)
    return jsonify(data)

if __name__ == "__main__":
  app.run(debug=False)
