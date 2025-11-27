import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VunaGuide API"
    # It will auto-read GOOGLE_CLOUD_PROJECT from .env
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID_HERE")
    LOCATION: str = "us-central1"
    MODEL_ID: str = os.getenv("MODEL_ID", "gemini-1.5-flash-002")
    
    # ✅ FIX 1: Define the missing variable
    ENV_STATE: str = "dev" 

    # ✅ FIX 2: Configuration to allow/ignore extra variables
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # This prevents crashes if .env has extra keys
    )

settings = Settings()