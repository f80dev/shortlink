import logging
import os

from flask import Flask, request, jsonify, redirect
from tools import get_url, add_url, find, _all

app = Flask(__name__)

@app.route("/api/admin/", methods=["GET"])
def admin_api():
  """
  test : http://x.f80.fr/api/admin/
  test: http://ipb2hoaif5bd77av6sahov5l2k.ingress.europlots.com/api/admin/
  test: http://127.0.0.1:5000/api/admin/
  :return:
  """
  rc=_all(1000)
  return jsonify({"urls":rc})


@app.route("/api/infos/", methods=["GET"])
def info_api():
  """
  test: http://127.0.0.1:5000/api/infos/
  :return:
  """
  return jsonify({"message":"ok"})




@app.route("/t<cid>", methods=["GET"])
@app.route("/api/add/", methods=["POST"])
def data(cid=""):
  if request.method == "GET":
    if cid=="favicon.ico": return jsonify({"message":"ok"})

    url=get_url(cid)

    format=request.args.get("format","redirect")
    if format=="json": return jsonify({"url":url} if len(url)>0 else {"Error":f"{cid} introuvable"})
    if format=="text": return url
    return redirect(url)


  elif request.method == "POST":
    #récupration des parametres
    url=request.json["url"]
    duration=request.json["duration"] if "duration" in request.json else 0
    service=request.json["service"] if "service" in request.json else ""

    logging.info(f"Création d'un lien {url} pour le service {service} avec une durée de validité de {duration}")
    data=add_url(url,service,prefix="t",duration=duration)
    return data

if __name__ == "__main__":
  app.run(debug=False,port=int(os.environ["PORT"]))
