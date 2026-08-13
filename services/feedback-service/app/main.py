from datetime import datetime,timezone
from fastapi import Depends,FastAPI,HTTPException,Query,Request,Response
from sqlalchemy import or_,select,text
from sqlalchemy.orm import Session
from .auth import Actor,actor_from_request
from .clients import send_notification
from .config import settings
from .database import get_db
from .domain import can_view,require_admin,require_staff,validate_transition
from .models import Audit,Comment,Feedback,StatusHistory
from .observability import RequestContextMiddleware,configure_logging,metrics_response
from .schemas import AssignRequest,CommentCreate,FeedbackCreate,FeedbackUpdate,OverrideRequest,StatusUpdate
from .service import add_audit,analytics_summary,apply_ai,distribution,serialize_feedback
configure_logging(settings.log_level);app=FastAPI(title="CampusPulse Feedback Service",version="2.0.0");app.add_middleware(RequestContextMiddleware,service_name="feedback-service")
def actor(request:Request):return actor_from_request(request)
@app.get("/health")
@app.get("/api/feedback/health")
def health():return {"status":"ok","service":"feedback-service","version":"2.0.0"}
@app.get("/ready")
def ready(db:Session=Depends(get_db)):
 try:db.execute(text("SELECT 1"));return {"status":"ready"}
 except Exception as exc:raise HTTPException(503,"database unavailable") from exc
@app.get("/metrics")
def metrics():return metrics_response()
@app.post("/api/feedback",status_code=201)
def create_feedback(payload:FeedbackCreate,request:Request,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=Feedback(created_by_user_id=a.id,**payload.model_dump());db.add(f);db.flush();apply_ai(db,f,request.state.request_id);add_audit(db,a.id,"feedback_created",f.id,{"ai_state":f.ai_analysis_state});db.commit();db.refresh(f);send_notification(a.id,f"Feedback submitted: {f.title}","FEEDBACK_SUBMITTED",f.id,request.state.request_id);return serialize_feedback(f)
@app.get("/api/feedback")
def list_feedback(a:Actor=Depends(actor),db:Session=Depends(get_db),status:str|None=None,priority:str|None=None,category:str|None=None,assigned:str|None=None,q:str|None=Query(default=None,max_length=100)):
 stmt=select(Feedback)
 if a.role=="STUDENT":stmt=stmt.where(Feedback.created_by_user_id==a.id)
 elif a.role=="STAFF":stmt=stmt.where(or_(Feedback.assigned_staff_id==a.id,Feedback.assigned_staff_id.is_(None)))
 if status:stmt=stmt.where(Feedback.status==status.upper())
 if priority:stmt=stmt.where(Feedback.final_priority==priority.upper())
 if category:stmt=stmt.where(Feedback.final_category==category.upper())
 if assigned=="me":stmt=stmt.where(Feedback.assigned_staff_id==a.id)
 if q:stmt=stmt.where(or_(Feedback.title.ilike(f"%{q}%"),Feedback.description.ilike(f"%{q}%"),Feedback.location.ilike(f"%{q}%")))
 return [serialize_feedback(x) for x in db.scalars(stmt.order_by(Feedback.created_at.desc()))]
def find_visible(feedback_id:str,a:Actor,db:Session)->Feedback:
 f=db.get(Feedback,feedback_id)
 if not f or not can_view(a,f):raise HTTPException(404,"Feedback not found")
 return f
@app.get("/api/feedback/{feedback_id}")
def get_feedback(feedback_id:str,a:Actor=Depends(actor),db:Session=Depends(get_db)):return serialize_feedback(find_visible(feedback_id,a,db))
@app.patch("/api/feedback/{feedback_id}")
def update_feedback(feedback_id:str,payload:FeedbackUpdate,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db)
 if a.role=="STUDENT" and f.status not in {"SUBMITTED","REOPENED"}:raise HTTPException(403,"Feedback cannot be edited after processing starts")
 for k,v in payload.model_dump(exclude_none=True).items():setattr(f,k,v)
 f.updated_at=datetime.now(timezone.utc);add_audit(db,a.id,"feedback_updated",f.id);db.commit();db.refresh(f);return serialize_feedback(f)
@app.delete("/api/feedback/{feedback_id}",status_code=204)
def delete_feedback(feedback_id:str,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db)
 if a.role!="ADMIN" and not (a.role=="STUDENT" and f.status=="SUBMITTED"):raise HTTPException(403,"Feedback cannot be deleted in its current state")
 db.delete(f);db.commit();return Response(status_code=204)
@app.patch("/api/feedback/{feedback_id}/assign")
def assign_feedback(feedback_id:str,payload:AssignRequest,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 require_staff(a);f=db.get(Feedback,feedback_id)
 if not f:raise HTTPException(404,"Feedback not found")
 f.assigned_staff_id=payload.staff_user_id
 if f.status=="SUBMITTED":f.status="ASSIGNED";db.add(StatusHistory(feedback_id=f.id,from_status="SUBMITTED",to_status="ASSIGNED",changed_by_user_id=a.id))
 add_audit(db,a.id,"feedback_assigned",f.id,{"assigned_staff_id":payload.staff_user_id});db.commit();db.refresh(f);return serialize_feedback(f)
@app.patch("/api/feedback/{feedback_id}/status")
def update_status(feedback_id:str,payload:StatusUpdate,request:Request,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 require_staff(a);f=db.get(Feedback,feedback_id)
 if not f:raise HTTPException(404,"Feedback not found")
 target=payload.status.value;validate_transition(f.status,target);old=f.status;f.status=target;f.updated_at=datetime.now(timezone.utc)
 if target=="RESOLVED":f.resolved_at=datetime.now(timezone.utc)
 if target=="REOPENED":f.resolved_at=None
 db.add(StatusHistory(feedback_id=f.id,from_status=old,to_status=target,changed_by_user_id=a.id));add_audit(db,a.id,"status_changed",f.id,{"from":old,"to":target});db.commit();db.refresh(f);send_notification(f.created_by_user_id,f"Issue status changed: {target}","STATUS_CHANGED",f.id,request.state.request_id);return serialize_feedback(f)
@app.post("/api/feedback/{feedback_id}/comments",status_code=201)
def add_comment(feedback_id:str,payload:CommentCreate,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db);c=Comment(feedback_id=f.id,user_id=a.id,user_role=a.role,body=payload.body);db.add(c);add_audit(db,a.id,"comment_added",f.id);db.commit();db.refresh(c);return {"id":c.id,"user_id":c.user_id,"user_role":c.user_role,"body":c.body,"created_at":c.created_at}
@app.get("/api/feedback/{feedback_id}/comments")
def list_comments(feedback_id:str,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db);return [{"id":c.id,"user_id":c.user_id,"user_role":c.user_role,"body":c.body,"created_at":c.created_at} for c in db.scalars(select(Comment).where(Comment.feedback_id==f.id).order_by(Comment.created_at))]
@app.post("/api/feedback/{feedback_id}/override")
def override_ai(feedback_id:str,payload:OverrideRequest,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 require_staff(a);f=db.get(Feedback,feedback_id)
 if not f:raise HTTPException(404,"Feedback not found")
 before={"category":f.final_category,"priority":f.final_priority}
 if payload.category:f.final_category=payload.category.value
 if payload.priority:f.final_priority=payload.priority.value
 f.human_override=True;f.override_reason=payload.reason;f.decision_source="HUMAN_OVERRIDE";add_audit(db,a.id,"ai_prediction_overridden",f.id,{"before":before,"after":{"category":f.final_category,"priority":f.final_priority},"reason":payload.reason});db.commit();db.refresh(f);return serialize_feedback(f)
@app.post("/api/feedback/{feedback_id}/retry-ai")
def retry_ai(feedback_id:str,request:Request,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db)
 if a.role=="STUDENT" and f.ai_analysis_state!="PENDING":raise HTTPException(403,"No pending AI analysis")
 apply_ai(db,f,request.state.request_id);add_audit(db,a.id,"ai_analysis_retried",f.id,{"state":f.ai_analysis_state});db.commit();db.refresh(f);return serialize_feedback(f)
@app.get("/api/feedback/{feedback_id}/history")
def history(feedback_id:str,a:Actor=Depends(actor),db:Session=Depends(get_db)):
 f=find_visible(feedback_id,a,db);return [{"from_status":h.from_status,"to_status":h.to_status,"changed_by_user_id":h.changed_by_user_id,"changed_at":h.changed_at} for h in db.scalars(select(StatusHistory).where(StatusHistory.feedback_id==f.id).order_by(StatusHistory.changed_at))]
def admin_actor(a:Actor):require_admin(a)
@app.get("/api/analytics/summary")
def analytics(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return analytics_summary(db)
@app.get("/api/analytics/categories")
def categories(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return distribution(db,Feedback.final_category)
@app.get("/api/analytics/priorities")
def priorities(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return distribution(db,Feedback.final_priority)
@app.get("/api/analytics/sentiment")
def sentiment(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return distribution(db,Feedback.ai_sentiment)
@app.get("/api/analytics/status")
def status_distribution(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return distribution(db,Feedback.status)
@app.get("/api/analytics/resolution-time")
def resolution_time(a:Actor=Depends(actor),db:Session=Depends(get_db)):admin_actor(a);return {"average_resolution_hours":analytics_summary(db)["average_resolution_hours"]}
@app.get("/api/audit")
def audit_view(a:Actor=Depends(actor),db:Session=Depends(get_db),limit:int=100):
 require_admin(a);rows=db.scalars(select(Audit).order_by(Audit.timestamp.desc()).limit(min(max(limit,1),500)));return [{c.name:getattr(r,c.name) for c in r.__table__.columns} for r in rows]
