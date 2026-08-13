import json,urllib.request,urllib.error
BASE="http://localhost:8080/api"
def post(path,payload,token=None,method="POST"):
 data=json.dumps(payload).encode();headers={"Content-Type":"application/json"}
 if token:headers["Authorization"]="Bearer "+token
 req=urllib.request.Request(BASE+path,data=data,headers=headers,method=method)
 with urllib.request.urlopen(req,timeout=10) as r:return json.loads(r.read())
student=post("/auth/login",{"email":"student@campuspulse.dev","password":"Student123!"})["access_token"]
examples=[{"title":"Exposed electrical wiring outside science laboratory","description":"Several exposed electrical wires are hanging next to the entrance and students are walking close to them.","location":"Science Laboratory entrance","department":"Facilities"},{"title":"Library Level 2 Wi-Fi instability","description":"The Wi-Fi in Library Level 2 disconnects every few minutes during study sessions.","location":"Library Level 2","department":"IT"},{"title":"Overflowing waste bins near cafeteria","description":"The bins beside the cafeteria have overflowed and the area requires cleaning.","location":"Main Cafeteria","department":"Facilities"}]
for item in examples:
 try:post("/feedback",item,student)
 except urllib.error.HTTPError as e:
  if e.code not in (409,422):raise
print("Demo feedback seed completed.")
