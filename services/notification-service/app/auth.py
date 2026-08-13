from fastapi import HTTPException,Request
import jwt
from .config import settings
def user_id(request:Request)->str:
 h=request.headers.get("Authorization","")
 if not h.startswith("Bearer "):raise HTTPException(401,"Authentication required")
 try:return jwt.decode(h[7:],settings.jwt_secret,algorithms=[settings.jwt_algorithm])["sub"]
 except Exception as exc:raise HTTPException(401,"Invalid or expired token") from exc
def require_internal(request:Request)->None:
 if request.headers.get("X-Service-Token")!=settings.internal_service_token:raise HTTPException(403,"Invalid service credential")
