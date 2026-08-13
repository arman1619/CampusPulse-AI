import uuid
from datetime import datetime,timezone
from sqlalchemy import Boolean,DateTime,String
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base
def now():return datetime.now(timezone.utc)
class Notification(Base):
 __tablename__="notifications"
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));user_id:Mapped[str]=mapped_column(String(36),index=True);message:Mapped[str]=mapped_column(String(500));event_type:Mapped[str]=mapped_column(String(60),default="GENERAL");resource_id:Mapped[str|None]=mapped_column(String(36),nullable=True);read:Mapped[bool]=mapped_column(Boolean,default=False,index=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True);read_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
