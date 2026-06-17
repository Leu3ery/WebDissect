from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RESEND_KEY: str = Field()
    JWT_ALGORITHM: str = Field()
    JWT_SECRET: str = Field()

    DB_FILENAME: str = Field()



@lru_cache
def get_settings() -> Settings:
    return Settings()