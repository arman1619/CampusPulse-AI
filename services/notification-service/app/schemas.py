from pydantic import BaseModel,Field
class InternalNotificationCreate(BaseModel):user_id:str=Field(min_length=36,max_length=36);message:str=Field(min_length=1,max_length=500);event_type:str=Field(default="GENERAL",max_length=60);resource_id:str|None=None
