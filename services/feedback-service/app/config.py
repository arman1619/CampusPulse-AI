from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 environment:str="development"
 log_level:str="INFO"
 feedback_database_url:str="sqlite:///./feedback.db"
 jwt_secret:str="change-me-local-only"
 jwt_algorithm:str="HS256"
 ai_service_url:str="http://ai-service:8003"
 notification_service_url:str="http://notification-service:8004"
 internal_service_token:str="change-me-internal"
 service_timeout_seconds:float=4.0
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
 @property
 def database_url(self):return self.feedback_database_url
settings=Settings()
