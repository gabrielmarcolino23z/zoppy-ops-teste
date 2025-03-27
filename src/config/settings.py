from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    
    # API Keys
    TAVILY_API_KEY: str = Field(..., json_schema_extra={"env": "TAVILY_API_KEY"})
    OPENAI_API_KEY: str = Field(..., json_schema_extra={"env": "OPENAI_API_KEY"})
    OPENAI_MODEL_NAME: str = Field(..., json_schema_extra={"env": "OPENAI_MODEL_NAME"})

    # JWT Settings
    JWT_SECRET_KEY: str = Field(..., json_schema_extra={"env": "JWT_SECRET_KEY"})
    JWT_SECRET_KEY_ALGORITHM: str = Field(..., json_schema_extra={"env": "JWT_SECRET_KEY_ALGORITHM"})

    # Database
    VECTOR_DB_PATH: str = Field(..., json_schema_extra={"env": "VECTOR_DB_PATH"})

    # LangSmith Settings
    LANGSMITH_PROJECT: str = Field(default="default", json_schema_extra={"env": "LANGSMITH_PROJECT"})

    # Other Settings
    SEED: int = Field(default=42, json_schema_extra={"env": "SEED"})

def get_settings() -> Settings:
    return Settings()