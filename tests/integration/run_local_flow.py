from __future__ import annotations
import json,os,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PY=sys.executable;SECRET="integration-jwt-secret-abcdefghijklmnopqrstuvwxyz-123456";INTERNAL="integration-service-secret-abcdefghijklmnopqrstuvwxyz"
services={"auth-service":8101,"feedback-service":8102,"ai-service":8103,"notification-service":8104,"assistant-service":8105};procs=[]
def request(method,url,payload=None,token=None):
 data=None if payload is None else json.dumps(payload).encode();headers={"Content-Type":"application/json","X-Request-ID":"integration-test-request"}
 if token:headers["Authorization"]="Bearer "+token
 req=urllib.request.Request(url,data=data,headers=headers,method=method)
 try:
  with urllib.request.urlopen(req,timeout=8) as r:return r.status,json.loads(r.read() or b"{}")
 except urllib.error.HTTPError as e:return e.code,json.loads(e.read() or b"{}")
def wait(url):
 for _ in range(80):
  try:
   with urllib.request.urlopen(url,timeout=1) as r:
    if r.status==200:return
  except Exception:time.sleep(.15)
 raise RuntimeError("service did not become healthy: "+url)
def run(cmd,cwd,env):subprocess.run(cmd,cwd=cwd,env=env,check=True,stdout=subprocess.DEVNULL)
def main():
 env=os.environ.copy();env.update({"JWT_SECRET":SECRET,"JWT_ALGORITHM":"HS256","INTERNAL_SERVICE_TOKEN":INTERNAL,"SEED_DEMO":"true","AUTH_DATABASE_URL":"sqlite:///./integration_auth.db","FEEDBACK_DATABASE_URL":"sqlite:///./integration_feedback.db","NOTIFICATION_DATABASE_URL":"sqlite:///./integration_notifications.db","ASSISTANT_DATABASE_URL":"sqlite:///./integration_assistant.db","ASSISTANT_BACKEND":"template","ASSISTANT_REQUIRE_LLM":"false","AI_BACKEND":"deterministic","AI_REQUIRE_LLM":"false","AI_SERVICE_URL":"http://127.0.0.1:8103","NOTIFICATION_SERVICE_URL":"http://127.0.0.1:8104"})
 for svc in ["auth-service","feedback-service","notification-service","assistant-service"]:
  cwd=ROOT/"services"/svc
  for db in cwd.glob("integration_*.db"):db.unlink(missing_ok=True)
  run([PY,"-m","alembic","upgrade","head"],cwd,env)
 run([PY,"-m","app.seed"],ROOT/"services/auth-service",env)
 try:
  for svc,port in services.items():
   cwd=ROOT/"services"/svc;p=subprocess.Popen([PY,"-m","uvicorn","app.main:app","--host","127.0.0.1","--port",str(port)],cwd=cwd,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);procs.append(p)
  for svc,port in services.items():wait(f"http://127.0.0.1:{port}/health")
  _,login=request("POST","http://127.0.0.1:8101/api/auth/login",{"email":"student@campuspulse.dev","password":"Student123!"});student=login["access_token"]
  _,staff_login=request("POST","http://127.0.0.1:8101/api/auth/login",{"email":"staff@campuspulse.dev","password":"Staff123!"});staff=staff_login["access_token"];staff_id=staff_login["user"]["id"]
  _,admin_login=request("POST","http://127.0.0.1:8101/api/auth/login",{"email":"admin@campuspulse.dev","password":"Admin123!"});admin=admin_login["access_token"]
  code,safety=request("POST","http://127.0.0.1:8102/api/feedback",{"title":"Exposed electrical wiring outside science laboratory","description":"Several exposed electrical wires are hanging next to the entrance and students are walking close to them.","location":"Science Lab"},student);assert code==201 and safety["final_priority"]=="CRITICAL" and safety["decision_source"]=="SAFETY_RULE" and safety["ai_analysis_state"]=="COMPLETE"
  code,wifi=request("POST","http://127.0.0.1:8102/api/feedback",{"title":"Library Wi-Fi instability","description":"The Wi-Fi in Library Level 2 disconnects every few minutes during study sessions.","location":"Library L2"},student);assert code==201 and wifi["final_priority"]!="CRITICAL"
  code,notes=request("GET","http://127.0.0.1:8104/api/notifications",token=student);assert code==200 and len(notes)>=2
  code,assigned=request("PATCH",f"http://127.0.0.1:8102/api/feedback/{safety['id']}/assign",{"staff_user_id":staff_id},staff);assert code==200 and assigned["status"]=="ASSIGNED"
  code,progress=request("PATCH",f"http://127.0.0.1:8102/api/feedback/{safety['id']}/status",{"status":"IN_PROGRESS"},staff);assert code==200 and progress["status"]=="IN_PROGRESS"
  code,over=request("POST",f"http://127.0.0.1:8102/api/feedback/{wifi['id']}/override",{"category":"IT","priority":"MEDIUM","reason":"Staff review confirms routine IT service degradation"},staff);assert code==200 and over["decision_source"]=="HUMAN_OVERRIDE"
  code,summary=request("GET","http://127.0.0.1:8102/api/analytics/summary",token=admin);assert code==200 and summary["total"]==2 and summary["ai_override_count"]==1
  code,assistant=request("POST","http://127.0.0.1:8105/api/assistant/chat",{"message":"How should I report a Wi-Fi issue in the library?"},student);assert code==200 and assistant["backend"]=="grounded-template" and len(assistant["citations"])>=1
  code,hazard=request("POST","http://127.0.0.1:8105/api/assistant/chat",{"message":"There are exposed electrical wires outside the laboratory."},student);assert code==200 and hazard["safety_notice"] and "emergency" in hazard["answer"].lower()
  print("LIVE INTEGRATION PASS: auth -> JWT -> feedback -> AI -> safety rule -> notification -> workflow -> override -> analytics -> assistant grounding/guardrail (deterministic CI backend)")
 finally:
  for p in reversed(procs):p.terminate()
  for p in reversed(procs):
   try:p.wait(timeout=4)
   except subprocess.TimeoutExpired:p.kill()
  for svc in ["auth-service","feedback-service","notification-service","assistant-service"]:
   for db in (ROOT/"services"/svc).glob("integration_*.db"):db.unlink(missing_ok=True)
if __name__=="__main__":main()
