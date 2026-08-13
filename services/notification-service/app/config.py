from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 environment:str="development";log_level:str="INFO";notification_database_url:str="sqlite:///./notifications.db";jwt_secret:str="change-me-local-only";jwt_algorithm:str="HS256";internal_service_token:str="change-me-internal"
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
 @property
 def database_url(self):return self.notification_database_url
settings=Settings()
