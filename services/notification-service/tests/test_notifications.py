from datetime import datetime,timedelta,timezone
import jwt
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app);uid="11111111-1111-1111-1111-111111111111"
def auth():return {"Authorization":"Bearer "+jwt.encode({"sub":uid,"role":"STUDENT","exp":datetime.now(timezone.utc)+timedelta(hours=1)},"test-secret-1234567890-abcdefghijklmnopqrstuvwxyz",algorithm="HS256")}
def test_notification_flow():
 payload={"user_id":uid,"message":"Feedback submitted","event_type":"FEEDBACK_SUBMITTED","resource_id":None};r=client.post("/internal/notifications",json=payload,headers={"X-Service-Token":"internal-test"});assert r.status_code==201;nid=r.json()["id"]
 assert client.get("/api/notifications/unread-count",headers=auth()).json()["unread_count"]==1
 assert client.patch(f"/api/notifications/{nid}/read",headers=auth()).json()["read"] is True
 assert client.get("/api/notifications/unread-count",headers=auth()).json()["unread_count"]==0
def test_internal_endpoint_rejects_missing_token():assert client.post("/internal/notifications",json={"user_id":uid,"message":"x"}).status_code==403
