import os
from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
    )

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication."
    )


    @field_validator("OPENAI_API_KEY")
    @classmethod
    def check_not_empty(cls, value:str, info) -> str:
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty.")
        
        return value
    

try:
    settings = Settings()

except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)