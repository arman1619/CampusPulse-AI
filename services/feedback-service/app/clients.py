import httpx
from .config import settings
def analyse_feedback(title:str,description:str,request_id:str)->dict:
 with httpx.Client(timeout=settings.service_timeout_seconds) as client:
  r=client.post(f"{settings.ai_service_url}/api/ai/analyse",json={"title":title,"description":description},headers={"X-Request-ID":request_id});r.raise_for_status();return r.json()
def send_notification(user_id:str,message:str,event_type:str,resource_id:str|None,request_id:str)->None:
 try:
  with httpx.Client(timeout=2.5) as client:client.post(f"{settings.notification_service_url}/internal/notifications",json={"user_id":user_id,"message":message,"event_type":event_type,"resource_id":resource_id},headers={"X-Request-ID":request_id,"X-Service-Token":settings.internal_service_token}).raise_for_status()
 except Exception:
  return
