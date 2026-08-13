from dataclasses import dataclass
from fastapi import HTTPException,Request
import jwt
from .config import settings
@dataclass(frozen=True)
class Actor:
 id:str;role:str;email:str|None=None
def actor_from_request(request:Request)->Actor:
 header=request.headers.get("Authorization","")
 if not header.startswith("Bearer "):raise HTTPException(401,"Authentication required")
 try:payload=jwt.decode(header[7:],settings.jwt_secret,algorithms=[settings.jwt_algorithm])
 except Exception as exc:raise HTTPException(401,"Invalid or expired token") from exc
 return Actor(id=payload["sub"],role=payload.get("role","STUDENT"),email=payload.get("email"))
