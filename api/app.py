import hashlib
import random
from base64 import b64encode

from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

db = MongoClient("mongodb://root:hh4271@192.168.1.62:27017/")["shortlinks"]
collection = db["links"]

def toBase64(n:int):
  nombre_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
  return b64encode(nombre_bytes).decode("ascii")


def find(cid:str,field="cid"):
  data = list(collection.find({field:cid}))
  if len(data)>0:
    return data[0]
  else:
    return None



def generate_cid(url:str) -> str:
  obj=find(url,"url")

  cid=obj["cid"] if obj else None
  if cid is None:
    while True:
      cid=toBase64(random.randint(1,9999999999))
      if find(cid) is None: break

  return cid


def add_url(url:str) -> dict:
  data={"cid":generate_cid(url),"url":url}
  if not data in collection:
    collection.insert_one(data)
  return data



@app.route("/api/<cid>", methods=["GET"])
@app.route("/api", methods=["POST"])
def data(cid=""):
  if request.method == "GET":

    data=find(cid)
    return jsonify(data if data else {"Error":f"{cid} introuvable"})

  elif request.method == "POST":
    data=add_url(request.json["url"])
    return jsonify(data)

if __name__ == "__main__":
  app.run(debug=False)
