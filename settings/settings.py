from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict

"""
load environment variable class
"""

class Settings(BaseSettings):
    MASTER_DB_OWNER:str
    MASTER_DB_PASSWORD:str
    MASTER_DB_HOST_NAME:str
    MASTER_DB_PORT:str
    MASTER_DB_NAME:str
    TEST_DB_PASSWORD:str
    TEST_DB_PORT:str
    TEST_DB_HOST_NAME:str
    TEST_DB_NAME:str
    SECRET_KEY:str
    TEST_DB_USERNAME:str
    model_config=SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings()->Settings:
    return Settings()