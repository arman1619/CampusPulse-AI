from datetime import datetime,timezone
from fastapi import Depends,FastAPI,HTTPException,Request
from sqlalchemy import func,select,text,update
from sqlalchemy.orm import Session
from .auth import require_internal,user_id
from .config import settings
from .database import get_db
from .models import Notification
from .observability import RequestContextMiddleware,configure_logging,metrics_response
from .schemas import InternalNotificationCreate
configure_logging(settings.log_level);app=FastAPI(title="CampusPulse Notification Service",version="2.0.0");app.add_middleware(RequestContextMiddleware,service_name="notification-service")
def serialize(n):return {"id":n.id,"user_id":n.user_id,"message":n.message,"event_type":n.event_type,"resource_id":n.resource_id,"read":n.read,"created_at":n.created_at,"read_at":n.read_at}
@app.get("/api/notifications/health")
@app.get("/health")
def health():return {"status":"ok","service":"notification-service","version":"2.0.0"}
@app.get("/ready")
def ready(db:Session=Depends(get_db)):
 try:db.execute(text("SELECT 1"));return {"status":"ready"}
 except Exception as exc:raise HTTPException(503,"database unavailable") from exc
@app.get("/metrics")
def metrics():return metrics_response()
@app.post("/internal/notifications",status_code=201)
def create_internal(payload:InternalNotificationCreate,request:Request,db:Session=Depends(get_db)):
 require_internal(request);n=Notification(**payload.model_dump());db.add(n);db.commit();db.refresh(n);return serialize(n)
@app.get("/api/notifications")
def notifications(request:Request,db:Session=Depends(get_db),unread_only:bool=False):
 uid=user_id(request);stmt=select(Notification).where(Notification.user_id==uid)
 if unread_only:stmt=stmt.where(Notification.read.is_(False))
 return [serialize(n) for n in db.scalars(stmt.order_by(Notification.created_at.desc()))]
@app.get("/api/notifications/unread-count")
def unread_count(request:Request,db:Session=Depends(get_db)):
 uid=user_id(request);count=db.scalar(select(func.count()).select_from(Notification).where(Notification.user_id==uid,Notification.read.is_(False))) or 0;return {"unread_count":count}
@app.patch("/api/notifications/{notification_id}/read")
def mark_read(notification_id:str,request:Request,db:Session=Depends(get_db)):
 uid=user_id(request);n=db.get(Notification,notification_id)
 if not n or n.user_id!=uid:raise HTTPException(404,"Notification not found")
 n.read=True;n.read_at=datetime.now(timezone.utc);db.commit();db.refresh(n);return serialize(n)
@app.patch("/api/notifications/read-all")
def mark_all_read(request:Request,db:Session=Depends(get_db)):
 uid=user_id(request);now=datetime.now(timezone.utc);result=db.execute(update(Notification).where(Notification.user_id==uid,Notification.read.is_(False)).values(read=True,read_at=now));db.commit();return {"updated":result.rowcount or 0}
