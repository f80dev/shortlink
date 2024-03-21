import json
import logging
import os
import ssl
import sys

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

from tools import get_url, add_url, _all, get_services, stats, init_services, del_service, get_links

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


@app.route("/api/delete_services/", methods=["GET"])
def del_services_api():
  """
  test: http://127.0.0.1:80/api/services/
  test: https://x.f80.fr:30630/api/services/
  :return:
  """
  password=request.args.get("password","")
  service_id=request.args.get("id","*")
  if password==(os.environ["PASSWORD"] if "PASSWORD" in os.environ else "4271"): del_service(service_id)
  return jsonify(get_services())



@app.route("/api/services/", methods=["GET"])
def services_api():
  """
  test: http://127.0.0.1:80/api/services/
  test: https://x.f80.fr:30630/api/services/
  :return:
  """
  return jsonify(get_services())


@app.route("/api/links/", methods=["GET"])
def links_api():
  """
  test: http://127.0.0.1:80/api/links/
  test: https://x.f80.fr:30630/api/links/
  :return:
  """
  return jsonify(get_links())




@app.route("/api/update_services/", methods=["GET"])
def api_update_services():
  """
  test: http://127.0.0.1:80/api/update_services/
  test: https://x.f80.fr:30630/api/update_services/?url=https://linkut.f80.fr/assets/services.yaml
  :return:
  """
  url=request.args.get("url","./static/services.yaml")
  init_services(url,replace=True)
  return jsonify(get_services())

@app.route("/api/help/", methods=["GET"])
def api_help():
  """
  test: http://127.0.0.1:80/api/update_services/
  test: https://x.f80.fr:30630/api/update_services/?url=https://linkut.f80.fr/assets/services.yaml
  :return:
  """
  help="pour raccourcir une url utiliser simplement POST sur /apo/add"
  return help



@app.route("/t<cid>", methods=["GET"])
def api_get(cid=""):
  #test http://localhost:80/tr1uHIQ==
  if cid=="favicon.ico": return jsonify({"message":"ok"})
  url=get_url(cid)
  if url is None: return "url introuvable",500

  format=request.args.get("format","redirect") if type(url)==str else "json"
  if format=="json": return jsonify({"url":url} if len(url)>0 else {"Error":f"{cid} introuvable"})

  url=url + ("?"+str(request.query_string,'utf8') if str(request.query_string,"utf8")!='' else "")
  if format=="text": return url
  return redirect(url)



@app.route("/api/add/", methods=["POST"])
def api_post():
  """
  Lecture de url raccourcis
  :param cid:
  :return: retourne les parametres stocké ou une redirection si les parametres stockés sont un object contenant redirect ou sont une url
  """
  #récupration des parametres
  assert "url" in request.json,"Auncune url à raccourcir"
  url=request.json["url"]
  logging.info("Demande de réduction de "+url+" avec data="+json.dumps(request.json["values"]))
  duration=request.json["duration"] if "duration" in request.json else 0

  logging.info(f"Création d'un lien {url} avec une durée de validité de {duration}")
  data=add_url(url,prefix="t",duration=duration,values=request.json["values"])
  return jsonify({"cid":data})



if __name__ == "__main__":
  port=(os.environ["PORT"] if "PORT" in os.environ else None) or (sys.argv[1] if len(sys.argv)>1 and sys.argv[1].isdigit() else None) or "80"
  init_services(os.environ["SERVICES_PATH"] if "SERVICES_PATH" in os.environ else "./static/services.yaml",replace=True)
  for service in get_services():
    logging.info("service "+service['service']+" disponible")

  with_ssl=((os.environ["SSL"] if "SSL" in os.environ else "False")=="True")
  if with_ssl:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #voir https://docs.python.org/3/library/ssl.html#ssl.SSLContext
    #conversion https://www.sslshopper.com/assets/snippets/sslshopper/ssl-converter.php
    #context.load_cert_chain(certfile="f80.fr_ssl_certificate.cer",keyfile="_.f80.fr_private_key.pem",password="hh4271")
    context.load_cert_chain(certfile="cert.pem",keyfile="key.pem")
    logging.info("chargement d'un contexte SSL")
    app.run(debug=False,host="0.0.0.0",port=int(port),ssl_context=context)
  else:
    logging.info("Connexion sans SSL sur port "+port)
    app.run(debug=True,host="0.0.0.0",port=int(port))
