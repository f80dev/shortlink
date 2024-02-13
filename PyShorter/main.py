import requests
data={
    "url":"http://liberation.fr"
}
r=requests.api.post("http://x.f80.fr/api/add/",data=data,headers={"Accept":"application/json"})
print(r.text)
