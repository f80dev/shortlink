from json import dumps
from time import sleep

from app import add_url, get_url, app
from tools import del_service, add_service, delete, find, _all, get_services, init_services


def test_init_services():
  del_service("redirect")
  init_services()
  services=get_services()
  assert len(services)>0

def test_load_services():
  add_service("gate","http://xgate.nfluent.io/?p=hjhfjdshjkfshdjkfhdsjkhfd&url={url}")
  services=get_services()
  assert len(services)>0
  del_service("servicetest")

def test_add_service():
  del_service("nftcheck")
  assert add_service("nftcheck","https://gate.nfluent.io/?url={url}")
  del_service("nftcheck")


def test_add_service_2(id="xgate"):
  false=False
  true=True
  del_service(id)
  body={"redirect":"lemonde.fr",
        "connexion":{"private_key":false,"keystore":false,"address":false,"direct_connect":false,"email":false,"extension_wallet":true,"google":false,"nfluent_wallet_connect":false,"on_device":false,"wallet_connect":true,"web_wallet":true,"webcam":false},
        "messages":{
          "intro":"L'accès a ce contenu est limité",
          "fail":"Impossible de continuez sans le NFT ou le paiement requis",
          "success":"Eligibilité vérifiée. Vous pouvez rejoindre le site"
        },
        "required":1,
        "network":"elrond-devnet",
        "store":"",
        "style":"color:white;background-color: #53576EFF;","bank":"",
        "price":"0.1",
        "merchant":{
          "contact":"",
          "country":"",
          "currency":"",
          "id":"",
          "name":"",
          "wallet":{"address":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
                    "token":"XEGLD-78ebc6","unity":"xEGLD","network":"elrond-devnet"}
        }
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
  url=get_url(cid,format="url")
  assert type(url)==dict
  assert "url" in url


def test_add_same_url():
  url="https://lemonde.fr"
  cid1=add_url(url)
  cid2=add_url(url)
  assert cid1==cid2


def test_admin():
  rc=_all()
  assert len(rc)>0


def test_find():
  url="https://liberation.fr"
  delete(url,"url")
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
  delete(url,"url")
  cid=add_url(url)
  redirect_url=get_url(cid)
  assert redirect_url==url



def test_add_url_with_service(url="https://lemonde.fr",service="nftcheck"):
  cid=add_url(url=url,service=service)
  assert len(cid)>0
  return cid




def test_get_url_with_service(url="https://nfluent.io"):
  test_add_service()
  cid=test_add_url_with_service(url,"nftcheck")
  result=get_url(cid)
  assert len(result)>0




def test_api_add_url(url="https://liberation.fr",duration=0):
  headers = {
    'Content-Type': "application/json",
    'Accept': "application/json"
  }

  data={"url":url,"duration":duration}
  response=app.test_client().post("/api/add/",data=dumps(data),headers=headers)

  assert len(response.text)>0
  return response.text


def test_api_get_url(url="https://lemonde.fr"):
  cid=test_api_add_url(url=url)
  response=app.test_client().get("/"+cid+"?format=text",headers={'Content-Type': "application/json"})
  assert response.text==url


def test_api_get_url_in_timeout(url="https://nfluent.io",duration=1):
  cid=test_api_add_url(url=url,duration=duration)
  sleep(62.0)
  response=app.test_client().get("/"+cid+"?format=text",headers={'Content-Type': "application/json"})
  assert response.text==""


