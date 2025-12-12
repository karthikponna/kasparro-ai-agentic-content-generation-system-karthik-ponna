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

    # LLM Configuration
    LLM_MODEL_NAME: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name to use for LLM calls."
    )

    LLM_TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature setting for LLM responses."
    )

    # Retry Configuration (Point 15)
    LLM_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for transient LLM errors."
    )
    
    LLM_RETRY_DELAY: float = Field(
        default=1.0,
        description="Delay in seconds between retries."
    )

    # Data Configuration
    PRODUCT_DATA_PATH: str = Field(
        default="data/product_data.json",
        description="Path to product data JSON file."
    )

    # Output Configuration
    OUTPUT_DIR: str = Field(
        default="output",
        description="Directory for output JSON files."
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