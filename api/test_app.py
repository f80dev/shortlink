import base64

from app import toBase64, generate_cid, add_url, find, delete


def test_add_same_url():
  url="https://lemonde.fr"
  cid1=add_url(url)["cid"]
  cid2=add_url(url)["cid"]
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


