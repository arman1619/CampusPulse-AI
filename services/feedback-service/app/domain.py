from fastapi import HTTPException
TRANSITIONS={"SUBMITTED":{"ASSIGNED"},"ASSIGNED":{"IN_PROGRESS"},"IN_PROGRESS":{"RESOLVED"},"RESOLVED":{"CLOSED","REOPENED"},"CLOSED":{"REOPENED"},"REOPENED":{"ASSIGNED","IN_PROGRESS"}}
def validate_transition(current:str,target:str)->None:
 if target not in TRANSITIONS.get(current,set()):raise HTTPException(409,f"Invalid transition {current} -> {target}")
def can_view(actor,feedback)->bool:
 if actor.role=="ADMIN":return True
 if actor.role=="STAFF":return feedback.assigned_staff_id in (None,actor.id)
 return feedback.created_by_user_id==actor.id
def require_staff(actor)->None:
 if actor.role not in {"STAFF","ADMIN"}:raise HTTPException(403,"Staff or admin role required")
def require_admin(actor)->None:
 if actor.role!="ADMIN":raise HTTPException(403,"Admin role required")
