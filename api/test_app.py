from app import add_url, find, delete, add_service, del_service, get_url


def test_add_service():
  del_service("nftcheck")
  assert add_service("nftcheck","https://gate.nfluent.io/?url={url}")


def test_add_same_url():
  url="https://lemonde.fr"
  cid1=add_url(url)
  cid2=add_url(url)
  assert cid1==cid2


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
  cid=add_url(url,service)
  assert len(cid)>0
  return cid

def test_get_url_with_service(url="https://nfluent.io"):
  test_add_service()
  cid=test_add_url_with_service(url,"nftcheck")
  result=get_url(cid)
  assert len(result)>0




