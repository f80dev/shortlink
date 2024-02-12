import logging
import os

from flask import Flask, request, jsonify, redirect
from tools import get_url, add_url, find, _all

app = Flask(__name__)

@app.route("/api/admin", methods=["GET"])
def admin_api():
  rc=_all(1000)
  return jsonify({"urls":rc})


@app.route("/<cid>", methods=["GET"])
@app.route("/api/add", methods=["POST"])
def data(cid=""):
  if request.method == "GET":
    format=request.args.get("format","redirect")
    url=get_url(cid)
    if format=="json":
      return jsonify({"url":url} if len(url)>0 else {"Error":f"{cid} introuvable"})

    return redirect(url)

  elif request.method == "POST":
    url=request.json["url"]
    service=request.json["service"] if "service" in request.json else ""
    logging.info(f"Création d'un lien {url} pour le service {service}")
    data=add_url(url,service)
    return jsonify(data)

if __name__ == "__main__":
  app.run(debug=False,port=int(os.environ["PORT"]))
