from json import dumps
from time import sleep

from app import add_url, get_url, app
from tools import del_service, add_service, delete, find, _all, get_services, REDIRECT_NAME

headers = {
  'Content-Type': "application/json",
  'Accept': "application/json"
}


def test_load_services():
  add_service("servicetest","http://xgate.nfluent.io/?p=hjhfjdshjkfshdjkfhdsjkhfd&url={url}")
  services=get_services()
  assert len(services)>0
  del_service("servicetest")

def test_add_service():
  del_service("nftcheck")
  assert add_service("nftcheck","https://gate.nfluent.io/?url={url}")


def test_add_json():
  body:dict={
    REDIRECT_NAME:"https://liberation.fr/",
    "p1":"10",
    "p2":20
  }
  cid=add_url(body)
  url=get_url(cid)
  assert url.startswith(body[REDIRECT_NAME])


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
  data={"url":url,"duration":duration}
  response=app.test_client().post("/api/add/",data=dumps(data),headers=headers)
  assert len(response.text)>0
  return response.text



def test_api_get_url_with_parameters(url="https://liberation.fr",duration=0,params="param1=1&param2=2"):
  data={"url":url,"duration":duration}
  result=app.test_client().post("/api/add/",data=dumps(data),headers=headers)
  cid=result.json["cid"]
  url_recup=app.test_client().get("/"+cid+"?"+params+"&format=text")
  assert params in url_recup.text




def test_api_get_url(url="https://lemonde.fr"):
  cid=add_url(url=url)
  response=app.test_client().get("/"+cid,headers=headers)
  assert response.text==url




def test_api_get_url_in_timeout(url="https://nfluent.io",duration=1):
  cid=test_api_add_url(url=url,duration=duration/60)
  sleep(duration/60+3)
  response=app.test_client().get("/"+cid+"?format=text",headers=headers)
  assert response.text==""
