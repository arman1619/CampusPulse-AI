from datetime import datetime,timedelta,timezone
import jwt
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def token(uid="11111111-1111-1111-1111-111111111111",role="STUDENT"):return jwt.encode({"sub":uid,"role":role,"exp":datetime.now(timezone.utc)+timedelta(hours=1)},"test-secret-1234567890-abcdefghijklmnopqrstuvwxyz",algorithm="HS256")
def test_student_crud_and_visibility():
 h={"Authorization":f"Bearer {token()}"};r=client.post("/api/feedback",json={"title":"Library Wi-Fi issue","description":"The Wi-Fi disconnects every few minutes","location":"Library L2"},headers=h);assert r.status_code==201;fid=r.json()["id"];assert r.json()["ai_analysis_state"]=="PENDING"
 assert client.get(f"/api/feedback/{fid}",headers=h).status_code==200
 other={"Authorization":f"Bearer {token('22222222-2222-2222-2222-222222222222')}"};assert client.get(f"/api/feedback/{fid}",headers=other).status_code==404
def test_workflow_override_and_analytics():
 student={"Authorization":f"Bearer {token()}"};fid=client.post("/api/feedback",json={"title":"Broken light","description":"A corridor light has stopped working near stairs"},headers=student).json()["id"]
 staff={"Authorization":f"Bearer {token('33333333-3333-3333-3333-333333333333','STAFF')}"};admin={"Authorization":f"Bearer {token('44444444-4444-4444-4444-444444444444','ADMIN')}"}
 assert client.patch(f"/api/feedback/{fid}/assign",json={"staff_user_id":"33333333-3333-3333-3333-333333333333"},headers=staff).json()["status"]=="ASSIGNED"
 assert client.patch(f"/api/feedback/{fid}/status",json={"status":"IN_PROGRESS"},headers=staff).status_code==200
 r=client.post(f"/api/feedback/{fid}/override",json={"priority":"HIGH","reason":"Inspection confirms immediate repair is needed"},headers=staff);assert r.json()["decision_source"]=="HUMAN_OVERRIDE"
 assert client.get("/api/analytics/summary",headers=admin).json()["ai_override_count"]==1
def test_student_cannot_change_status():
 h={"Authorization":f"Bearer {token()}"};fid=client.post("/api/feedback",json={"title":"Parking sign","description":"Parking sign is difficult to read at night"},headers=h).json()["id"]
 assert client.patch(f"/api/feedback/{fid}/status",json={"status":"ASSIGNED"},headers=h).status_code==403
