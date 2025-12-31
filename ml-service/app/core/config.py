"""ML Service Configuration."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """ML Service settings."""
    
    APP_NAME: str = "SecurePay ML Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Model paths
    MODEL_DIR: str = Field(default="./models", env="MODEL_DIR")
    
    # Model settings
    ENSEMBLE_WEIGHTS: list = [0.35, 0.40, 0.25]  # RF, XGB, NN
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Feature engineering
    N_FEATURES: int = 45
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
