import json
from datetime import datetime,timezone
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from . import clients
from .models import Audit,Comment,Feedback,StatusHistory
def serialize_feedback(f:Feedback)->dict:return {c.name:getattr(f,c.name) for c in f.__table__.columns}
def add_audit(db:Session,actor_id:str,action:str,resource_id:str,metadata:dict|None=None)->None:db.add(Audit(actor_user_id=actor_id,action=action,resource_type="feedback",resource_id=resource_id,metadata_json=json.dumps(metadata or {},sort_keys=True)))
def apply_ai(db:Session,f:Feedback,request_id:str)->None:
 try:
  a=clients.analyse_feedback(f.title,f.description,request_id);f.ai_category=a["category"]["label"];f.ai_category_confidence=a["category"]["confidence"];f.ai_sentiment=a["sentiment"]["label"];f.ai_sentiment_confidence=a["sentiment"]["confidence"];f.ai_priority=a["priority"]["label"];f.ai_priority_confidence=a["priority"]["confidence"];f.ai_model_version=a["model_version"];f.ai_needs_review=a["needs_review"];f.final_category=f.ai_category;f.final_priority=f.ai_priority;f.decision_source=a["decision_source"];f.ai_analysis_state="COMPLETE"
 except Exception:f.ai_analysis_state="PENDING";f.ai_needs_review=True
def distribution(db:Session,column):return [{"label":label or "UNKNOWN","count":count} for label,count in db.execute(select(column,func.count()).group_by(column)).all()]
def analytics_summary(db:Session)->dict:
 rows=list(db.scalars(select(Feedback)));resolved=[x for x in rows if x.resolved_at];avg=sum((x.resolved_at-x.created_at).total_seconds() for x in resolved)/len(resolved)/3600 if resolved else 0
 return {"total":len(rows),"open":sum(x.status not in {"RESOLVED","CLOSED"} for x in rows),"in_progress":sum(x.status=="IN_PROGRESS" for x in rows),"resolved":sum(x.status in {"RESOLVED","CLOSED"} for x in rows),"critical":sum(x.final_priority=="CRITICAL" for x in rows),"ai_override_count":sum(x.human_override for x in rows),"review_required_count":sum(x.ai_needs_review for x in rows),"average_resolution_hours":round(avg,2)}
