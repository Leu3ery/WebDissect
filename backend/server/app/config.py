from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    RESEND_KEY: str = Field()
    JWT_ALGORITHM: str = Field()
    JWT_SECRET: str = Field()

    DB_FILENAME: str = Field()
    HAR_STORAGE_DIR: str = Field()



@lru_cache
def get_settings() -> Settings:
    return Settings()