from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.service import create_user
client=TestClient(app)
def test_register_login_and_me():
    r=client.post("/api/auth/register",json={"email":"a@example.com","full_name":"Alice Student","password":"StrongPass1!"}); assert r.status_code==201
    r=client.post("/api/auth/login",json={"email":"a@example.com","password":"StrongPass1!"}); assert r.status_code==200; token=r.json()["access_token"]
    r=client.get("/api/auth/me",headers={"Authorization":f"Bearer {token}"}); assert r.status_code==200 and r.json()["role"]=="STUDENT"
def test_admin_role_and_disable_audit():
    with SessionLocal() as db:
        admin=create_user(db,"admin@example.com","Admin User","AdminPass1!","ADMIN"); student=create_user(db,"s@example.com","Student User","StudentPass1!","STUDENT")
    token=client.post("/api/auth/login",json={"email":"admin@example.com","password":"AdminPass1!"}).json()["access_token"]
    h={"Authorization":f"Bearer {token}"}
    assert client.patch(f"/api/auth/users/{student.id}/role",json={"role":"STAFF"},headers=h).json()["role"]=="STAFF"
    assert client.patch(f"/api/auth/users/{student.id}/active",json={"active":False},headers=h).json()["active"] is False
    audit=client.get("/api/auth/audit",headers=h); assert audit.status_code==200 and len(audit.json())>=2
def test_non_admin_cannot_list_users():
    client.post("/api/auth/register",json={"email":"s@example.com","full_name":"Student User","password":"StudentPass1!"})
    token=client.post("/api/auth/login",json={"email":"s@example.com","password":"StudentPass1!"}).json()["access_token"]
    assert client.get("/api/auth/users",headers={"Authorization":f"Bearer {token}"}).status_code==403
