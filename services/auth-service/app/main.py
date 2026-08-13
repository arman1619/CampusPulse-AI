from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .dependencies import current_user, require_admin
from .models import AuthAudit, User
from .observability import RequestContextMiddleware, configure_logging, metrics_response
from .schemas import ActiveUpdate, LoginRequest, LoginResponse, RegisterRequest, RoleUpdate, UserResponse
from .security import create_token
from .service import audit, authenticate, create_user
configure_logging(settings.log_level)
app=FastAPI(title="CampusPulse Auth Service",version="2.0.0")
app.add_middleware(RequestContextMiddleware,service_name="auth-service")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],allow_credentials=False,allow_methods=["*"],allow_headers=["Authorization","Content-Type","X-Request-ID"])
@app.get("/health")
@app.get("/api/auth/health")
def health(): return {"status":"ok","service":"auth-service","version":"2.0.0"}
@app.get("/ready")
def ready(db:Session=Depends(get_db)):
    try: db.execute(text("SELECT 1")); return {"status":"ready"}
    except Exception as exc: raise HTTPException(503,"database unavailable") from exc
@app.get("/metrics")
def metrics(): return metrics_response()
@app.post("/api/auth/register",response_model=UserResponse,status_code=201)
def register(payload:RegisterRequest,db:Session=Depends(get_db)):
    try: user=create_user(db,payload.email,payload.full_name,payload.password)
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc
    audit(db,user.id,"user_registered",user.id); return user
@app.post("/api/auth/login",response_model=LoginResponse)
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    user=authenticate(db,payload.email,payload.password)
    if not user: raise HTTPException(401,"Invalid credentials")
    return LoginResponse(access_token=create_token(user),user=UserResponse.model_validate(user))
@app.get("/api/auth/me",response_model=UserResponse)
def me(user:User=Depends(current_user)): return user
@app.get("/api/auth/users",response_model=list[UserResponse])
def users(_:User=Depends(require_admin),db:Session=Depends(get_db)): return list(db.scalars(select(User).order_by(User.created_at.desc())))
@app.patch("/api/auth/users/{user_id}/role",response_model=UserResponse)
def update_role(user_id:str,payload:RoleUpdate,admin:User=Depends(require_admin),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"User not found")
    old=user.role; user.role=payload.role.value; db.commit(); db.refresh(user); audit(db,admin.id,"user_role_changed",user.id,{"from":old,"to":user.role}); return user
@app.patch("/api/auth/users/{user_id}/active",response_model=UserResponse)
def update_active(user_id:str,payload:ActiveUpdate,admin:User=Depends(require_admin),db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"User not found")
    if user.id==admin.id and not payload.active: raise HTTPException(400,"Admin cannot disable own account")
    user.active=payload.active; db.commit(); db.refresh(user); audit(db,admin.id,"account_enabled" if payload.active else "account_disabled",user.id); return user
@app.get("/api/auth/audit")
def auth_audit(_:User=Depends(require_admin),db:Session=Depends(get_db),limit:int=100):
    rows=db.scalars(select(AuthAudit).order_by(AuthAudit.timestamp.desc()).limit(min(max(limit,1),500)))
    return [{"id":r.id,"actor_user_id":r.actor_user_id,"action":r.action,"resource_id":r.resource_id,"metadata_json":r.metadata_json,"timestamp":r.timestamp} for r in rows]
