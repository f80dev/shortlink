import base64

from app import toBase64, generate_cid, add_url


def test_toBase64():
  for n in range(100000,1000000000,10000):
    code=toBase64(n)
    print(base64.b64decode())

def test_add_same_url():
  url="https://lemonde.fr"
  cid1=add_url(url)["cid"]
  cid2=add_url(url)["cid"]
  assert cid1==cid2

def test_add_url():
  rc=[]
  for i in range(5):
    url=f"https://lemonde{i}.fr"
    cid=generate_cid(url)
    assert cid not in rc
    rc.append(cid)


