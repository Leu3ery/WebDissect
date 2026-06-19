from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Email (OTP delivery)
    RESEND_KEY: str = Field(default="RESEND_KEY")
    RESEND_FROM: str = Field(default="WebDissect <onboarding@resend.dev>")

    # Auth / JWT
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_SECRET: str = Field(default="JWT_SECRET")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)

    # OTP
    OTP_EXPIRE_MINUTES: int = Field(default=10)
    OTP_MAX_ATTEMPTS: int = Field(default=5)

    # Only school emails may register / login (NA03)
    EMAIL_DOMAIN: str = Field(default="htlstp.at")

    # Database
    DB_FILENAME: str = Field(default="webdissect.db")
    # Directory that holds the sqlite file. /app/db inside the container,
    # a local ./db folder when running outside of docker.
    DB_DIR: str = Field(default="/app/db")

    # Runtime
    ENV: str = Field(default="development")

    # CORS origins allowed to call the API directly (dev convenience)
    CORS_ORIGINS: str = Field(
        default="http://localhost:4200,http://localhost:8080,http://localhost"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
