from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field


def build_scheduler_db(fields: dict):
    db_url: PostgresDsn = fields["DATABASE_URL"]

    scheme = str(db_url).replace("+asyncpg", "")
    return scheme


class Settings(BaseSettings):
    DEBUG: bool = True
    TITLE: str = "Auction API"
    VERSION: str = "1.0.0"
    DATABASE_URL: PostgresDsn
    SCHEDULER_DATABASE_URL: PostgresDsn = Field(default_factory=build_scheduler_db)
    DEFAULT_BID_DURATION_SECONDS: int = 12


settings = Settings()
