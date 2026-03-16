from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
"""
load environment variable class
"""

class Settings:
    MASTER_DB_OWNER:str
    MASTER_DB_PASSWORD:str
    MASTER_DB_HOST_NAME:str
    MASTER_DB_PORT:str
    MASTER_DB_NAME:str
    SECRET_KEY:str
    model_config=SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings()->Settings:
    return Settings()