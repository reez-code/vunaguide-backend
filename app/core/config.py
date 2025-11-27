import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VunaGuide API"
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
    LOCATION: str = "us-central1"
    MODEL_ID: str = "gemini-2.0-flash-exp"
    
    class Config:
        env_file = ".env"

settings = Settings()