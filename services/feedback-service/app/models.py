import uuid
from datetime import datetime,timezone
from sqlalchemy import Boolean,DateTime,Float,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base
def now():return datetime.now(timezone.utc)
class Feedback(Base):
 __tablename__="feedback"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
 created_by_user_id:Mapped[str]=mapped_column(String(36),index=True)
 title:Mapped[str]=mapped_column(String(200));description:Mapped[str]=mapped_column(Text);location:Mapped[str]=mapped_column(String(200),default="");department:Mapped[str]=mapped_column(String(120),default="")
 status:Mapped[str]=mapped_column(String(30),default="SUBMITTED",index=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True);updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now);resolved_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 assigned_staff_id:Mapped[str|None]=mapped_column(String(36),nullable=True,index=True)
 ai_category:Mapped[str|None]=mapped_column(String(30),nullable=True);ai_category_confidence:Mapped[float|None]=mapped_column(Float,nullable=True);ai_sentiment:Mapped[str|None]=mapped_column(String(30),nullable=True);ai_sentiment_confidence:Mapped[float|None]=mapped_column(Float,nullable=True);ai_priority:Mapped[str|None]=mapped_column(String(30),nullable=True);ai_priority_confidence:Mapped[float|None]=mapped_column(Float,nullable=True);ai_model_version:Mapped[str|None]=mapped_column(String(80),nullable=True);ai_needs_review:Mapped[bool]=mapped_column(Boolean,default=True)
 final_category:Mapped[str|None]=mapped_column(String(30),nullable=True,index=True);final_priority:Mapped[str|None]=mapped_column(String(30),nullable=True,index=True);human_override:Mapped[bool]=mapped_column(Boolean,default=False);override_reason:Mapped[str|None]=mapped_column(Text,nullable=True);decision_source:Mapped[str]=mapped_column(String(30),default="MODEL");ai_analysis_state:Mapped[str]=mapped_column(String(20),default="PENDING")
class Comment(Base):
 __tablename__="comments"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));feedback_id:Mapped[str]=mapped_column(String(36),index=True);user_id:Mapped[str]=mapped_column(String(36));user_role:Mapped[str]=mapped_column(String(20));body:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class StatusHistory(Base):
 __tablename__="status_history"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));feedback_id:Mapped[str]=mapped_column(String(36),index=True);from_status:Mapped[str|None]=mapped_column(String(30),nullable=True);to_status:Mapped[str]=mapped_column(String(30));changed_by_user_id:Mapped[str]=mapped_column(String(36));changed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Audit(Base):
 __tablename__="audit"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));actor_user_id:Mapped[str]=mapped_column(String(36));action:Mapped[str]=mapped_column(String(80),index=True);resource_type:Mapped[str]=mapped_column(String(40));resource_id:Mapped[str]=mapped_column(String(36));metadata_json:Mapped[str]=mapped_column(Text,default="{}");timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)
