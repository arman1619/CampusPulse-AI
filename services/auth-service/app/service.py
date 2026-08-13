import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import AuthAudit, User
from .security import hash_password, verify_password
def create_user(db:Session,email:str,full_name:str,password:str,role:str="STUDENT")->User:
    normalized=email.strip().lower()
    if db.scalar(select(User).where(User.email==normalized)): raise ValueError("Email already registered")
    user=User(email=normalized,full_name=full_name.strip(),password_hash=hash_password(password),role=role); db.add(user); db.commit(); db.refresh(user); return user
def authenticate(db:Session,email:str,password:str)->User|None:
    user=db.scalar(select(User).where(User.email==email.strip().lower()))
    return user if user and user.active and verify_password(password,user.password_hash) else None
def audit(db:Session,actor_id:str|None,action:str,resource_id:str,metadata:dict|None=None)->None:
    db.add(AuthAudit(actor_user_id=actor_id,action=action,resource_id=resource_id,metadata_json=json.dumps(metadata or {},sort_keys=True))); db.commit()
