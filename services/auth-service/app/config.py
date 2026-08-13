from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    environment:str="development"
    log_level:str="INFO"
    auth_database_url:str="sqlite:///./auth.db"
    jwt_secret:str="change-me-local-only"
    jwt_algorithm:str="HS256"
    jwt_expire_minutes:int=60
    cors_origins:str="http://localhost:8080"
    seed_demo:bool=False
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    @property
    def database_url(self)->str:return self.auth_database_url
settings=Settings()
