from pydantic import BaseModel,Field
class AnalyseRequest(BaseModel):title:str=Field(min_length=1,max_length=200);description:str=Field(min_length=1,max_length=5000)
class Prediction(BaseModel):label:str;confidence:float
class AnalyseResponse(BaseModel):sentiment:Prediction;category:Prediction;priority:Prediction;needs_review:bool;decision_source:str;model_version:str;safety_rule:str|None=None
