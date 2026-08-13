from enum import Enum
from pydantic import BaseModel,Field
class FeedbackStatus(str,Enum):SUBMITTED="SUBMITTED";ASSIGNED="ASSIGNED";IN_PROGRESS="IN_PROGRESS";RESOLVED="RESOLVED";CLOSED="CLOSED";REOPENED="REOPENED"
class Category(str,Enum):IT="IT";FACILITIES="FACILITIES";CLEANLINESS="CLEANLINESS";SECURITY="SECURITY";LIBRARY="LIBRARY";PARKING="PARKING";ACADEMIC="ACADEMIC";ACCESSIBILITY="ACCESSIBILITY";OTHER="OTHER"
class Priority(str,Enum):LOW="LOW";MEDIUM="MEDIUM";HIGH="HIGH";CRITICAL="CRITICAL"
class FeedbackCreate(BaseModel):title:str=Field(min_length=3,max_length=200);description:str=Field(min_length=10,max_length=5000);location:str=Field(default="",max_length=200);department:str=Field(default="",max_length=120)
class FeedbackUpdate(BaseModel):title:str|None=Field(default=None,min_length=3,max_length=200);description:str|None=Field(default=None,min_length=10,max_length=5000);location:str|None=Field(default=None,max_length=200);department:str|None=Field(default=None,max_length=120)
class StatusUpdate(BaseModel):status:FeedbackStatus
class CommentCreate(BaseModel):body:str=Field(min_length=1,max_length=2000)
class OverrideRequest(BaseModel):category:Category|None=None;priority:Priority|None=None;reason:str=Field(min_length=8,max_length=1000)
class AssignRequest(BaseModel):staff_user_id:str=Field(min_length=36,max_length=36)
