import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    full_name:Mapped[str]=mapped_column(String(120))
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[str]=mapped_column(String(20),default="STUDENT",index=True)
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class AuthAudit(Base):
    __tablename__="auth_audit"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    actor_user_id:Mapped[str|None]=mapped_column(String(36),nullable=True)
    action:Mapped[str]=mapped_column(String(80),index=True)
    resource_id:Mapped[str]=mapped_column(String(36))
    metadata_json:Mapped[str]=mapped_column(Text,default="{}")
    timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)
