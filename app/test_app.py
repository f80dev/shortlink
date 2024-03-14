from json import dumps
from time import sleep

from app import add_url, get_url, app
from secret import TRANSFER_APP
from tools import del_service, add_service, del_link, find, _all, get_services, init_services, convert_dict_to_url

headers = {
  'Content-Type': "application/json",
  'Accept': "application/json"
}

REPLACE_VALUES={
  "address":"@herve",
  "token":"NFLUCOIN",
  "quantity":5
}
GATE_SERVICE="poh"


def test_convert_dict_to_url():
  d={"url":"http://lemonde.fr","p1":"v1","p2":"v2"}
  url=convert_dict_to_url(d,"url",convert_mode="param")
  assert url==d["url"]+"?p1=v1&p2=v2"

  url=convert_dict_to_url(d,"url",convert_mode="base64")
  assert url.startswith(d["url"]+"?b=")

def test_raz():
  del_service("*")
  del_link("*")


def test_init_services():
  init_services(replace=True)
  services=get_services()
  assert len(services)>0

def test_load_services(id="servicetest"):
  add_service("gate",{"domain":TRANSFER_APP},id)
  services=get_services()
  assert len(services)>0
  del_service(id)

def test_add_service(id="nftcheck"):
  del_service(id)
  assert add_service("nftcheck",{"domain":"https://gate.nfluent.io/"},id)
  del_service(id)


def test_add_service_2(id=GATE_SERVICE):
  false=False
  true=True
  del_service(id)
  body={"url":"lemonde.fr",
        "domain":TRANSFER_APP,
        "intro":"L'accès a ce contenu est limité",
        "fail":"Impossible de continuez sans le NFT ou le paiement requis",
        "success":"Eligibilité vérifiée. Vous pouvez rejoindre le site",
        "required":1,
        "network":"elrond-devnet",
        "store":"",
        "style":"color:white;background-color: #53576EFF;","bank":"",
        "price":"0.1",
        "address":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        "token":"XEGLD-78ebc6",
        "unity":"xEGLD"
      }
  rc=add_service("xGate",body,id,"Facturer un acces")
  assert rc

def test_add_json():
  body={
    "url":"https://liberation.fr/",
    "p1":"10",
    "p2":20
  }
  cid=add_url(body)
  url=get_url(cid)
  assert url.startswith(body["url"])


def test_add_same_url():
  test_init_services()
  url="https://lemonde.fr"
  cid1=add_url(url)
  cid2=add_url(url)
  assert cid1==cid2


def test_admin():
  rc=_all()
  assert len(rc)>0


def test_find():
  url="https://liberation.fr"
  del_link(url, "url")
  data=find(url,"url")
  assert data is None
  add_url(url)
  data=find(url,"url")
  assert data["url"]==url


def test_add_url():
  rc=[]
  for i in range(5):
    url=f"https://lemonde{i}.fr"
    data=add_url(url)
    assert data not in rc
    rc.append(data)



def test_add_url_without_service(url="https://liberation.fr"):
  del_link(url, "url")
  cid=add_url(url)
  redirect_url=get_url(cid)
  assert redirect_url==url



def test_add_url_with_service(url="https://lemonde.fr",service=GATE_SERVICE,values={}):
  del_link(url, "url")
  cid=add_url(url=url,service_id=service,values=values)
  assert len(cid)>0
  return cid


def test_add_url_with_service_and_values(url="https://leparisien.fr",service=GATE_SERVICE,values=REPLACE_VALUES):
  cid=add_url(url=url,service_id=service,values=values)
  assert len(cid)>0





def test_get_url_with_service(url="https://nfluent.io"):
  test_add_service()
  cid=test_add_url_with_service(url,GATE_SERVICE)
  url=get_url(cid)
  assert len(url)>0
  # obj=json.loads(base64.b64decode(url.split("b=")[1]))
  # assert "message" in obj
  # assert "domain" in obj
  return url


def test_get_same_url_with_differentvalues(url="http://lemonde2.fr",service="TokenGate"):
  values1={"address":"erd1"}
  values2={"address":"erd2"}
  cid1=test_add_url_with_service(url,service,values1)
  cid2=test_add_url_with_service(url,service,values2)
  assert cid1!=cid2


def test_get_same_url_with_samevalues(url="http://lemonde2.fr",service="TokenGate"):
  values={"address":"erd1"}
  cid1=test_add_url_with_service(url,service,values)
  cid2=test_add_url_with_service(url,service,values)
  assert cid1==cid2






def test_api_add_url(url="https://liberation.fr",duration=0,values=REPLACE_VALUES,id=GATE_SERVICE) -> str:
  data={"url":url,"duration":duration,"values":values,"service":id}
  response=app.test_client().post("/api/add/",data=dumps(data),headers=headers)

  assert len(response.text)>0

  cid=response.json["cid"]
  url=get_url(cid[1:])
  assert len(url)>0
  return cid




def test_api_get_url_out_timeout(url="https://nfluent.io",duration=1):
  cid=test_api_add_url(url=url,duration=duration)
  sleep(duration*10)
  response=app.test_client().get("/"+cid+"?format=json",headers=headers)
  assert response.status.startswith("500")
  assert del_link(cid,"cid")

def test_api_get_url_in_timeout(url="https://nfluent.io",duration=1):
  cid=test_api_add_url(url=url,duration=duration*3)
  sleep(duration)
  response=app.test_client().get("/"+cid+"?format=json",headers=headers)
  assert response.status=="200 OK"
  assert del_link(cid,"cid")




def test_api_get_url(url="https://lemonde.fr"):
  cid=test_api_add_url(url=url)
  response=app.test_client().get("/"+cid,headers=headers)
  assert response.status=="302 FOUND"
  return cid
