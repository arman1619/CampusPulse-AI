from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token
def current_user(request:Request,db:Session=Depends(get_db))->User:
    header=request.headers.get("Authorization","")
    if not header.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    try: payload=decode_token(header[7:]); user=db.get(User,payload["sub"])
    except Exception as exc: raise HTTPException(401,"Invalid or expired token") from exc
    if not user or not user.active: raise HTTPException(401,"Account unavailable")
    return user
def require_admin(user:User=Depends(current_user))->User:
    if user.role!="ADMIN": raise HTTPException(403,"Admin role required")
    return user
