import base64
import logging
import os
import ssl
import sys
from json import dump, dumps
from urllib.parse import urlparse

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

from tools import get_url, add_url, _all, get_services, stats, init_services

app = Flask(__name__)
CORS(app)


@app.route("/api/admin/", methods=["GET"])
def admin_api():
  """
  test : http://t.f80.fr/api/admin/
  test: http://ipb2hoaif5bd77av6sahov5l2k.ingress.europlots.com/api/admin/
  test: http://127.0.0.1:5000/api/admin/
  test: https://192.168.1.62/api/admin/   dans ce cas le port exposé est 443
  :return:
  """
  rc=_all(1000)
  return jsonify({"urls":rc})


@app.route("/api/infos/", methods=["GET"])
def info_api():

  """
  test: http://127.0.0.1:5000/api/infos/
  test: https://192.168.1.62/api/infos/   dans ce cas le port exposé est 443
  test: https://api.f80.fr/api/infos/   dans ce cas le port exposé est 443

  :return:
  """
  return jsonify({"statistiques":stats})


@app.route("/api/services/", methods=["GET"])
def services_api():
  """
  test: http://127.0.0.1:80/api/services/
  :return:
  """
  return jsonify(get_services())



@app.route("/t<cid>", methods=["GET"])
@app.route("/api/add/", methods=["POST"])
def ap_get(cid=""):
  """
  Lecture de url raccourcis
  :param cid:
  :return: retourne les parametres stocké ou une redirection si les parametres stockés sont un object contenant redirect ou sont une url
  """
  if request.method == "GET":
    #test http://localhost:80/tr1uHIQ==
    if cid=="favicon.ico": return jsonify({"message":"ok"})
    url=get_url(cid)

    format=request.args.get("format","redirect") if type(url)==str else "json"
    if format=="json": return jsonify({"url":url} if len(url)>0 else {"Error":f"{cid} introuvable"})

    url=url + ("?"+str(request.query_string,'utf8') if str(request.query_string,"utf8")!='' else "")
    if format=="text": return url
    return redirect(url)

  if request.method == "POST":
    #récupration des parametres
    url=request.json["url"]
    duration=request.json["duration"] if "duration" in request.json else 0
    service=request.json["service"] if "service" in request.json else ""

    logging.info(f"Création d'un lien {url} pour le service {service} avec une durée de validité de {duration}")
    data=add_url(url,service,prefix="t",duration=duration)
    return jsonify({"cid":data})




if __name__ == "__main__":
  port=(os.environ["PORT"] if "PORT" in os.environ else None) or (sys.argv[1] if len(sys.argv)>1 and sys.argv[1].isdigit() else None) or "8080"
  init_services()
  if "ssl" in sys.argv:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #voir https://docs.python.org/3/library/ssl.html#ssl.SSLContext
    #conversion https://www.sslshopper.com/assets/snippets/sslshopper/ssl-converter.php
    #context.load_cert_chain(certfile="f80.fr_ssl_certificate.cer",keyfile="_.f80.fr_private_key.pem",password="hh4271")
    context.load_cert_chain(certfile="cert.pem",keyfile="key.pem")
    app.run(debug=False,host="0.0.0.0",port=int(port),ssl_context=context)
  else:
    logging.info("Connexion sans SSL sur port "+port)
    app.run(debug=True,host="0.0.0.0",port=int(port))
