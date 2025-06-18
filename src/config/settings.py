"""
Application Configuration Settings
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings using Pydantic"""
    
    # Application Info
    APP_NAME: str = "AI Trading Overlay"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Reddit API
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "vidlah_trading_overlay_1.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./trading_data.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Screen Capture
    CAPTURE_INTERVAL: int = 5  # seconds
    DEFAULT_CAPTURE_REGION: str = "0,0,1920,1080"
    CHART_DETECTION_THRESHOLD: float = 0.8
    
    # AI Models
    PATTERN_CONFIDENCE_THRESHOLD: float = 0.7
    SENTIMENT_WEIGHT: float = 0.3
    TECHNICAL_WEIGHT: float = 0.7
    PREDICTION_INTERVAL: int = 60  # seconds
    
    # Network
    WEBSOCKET_PORT: int = 8000
    FRONTEND_PORT: int = 3000
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.MODELS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    @property
    def capture_region(self) -> tuple:
        """Parse capture region string to tuple"""
        x, y, w, h = map(int, self.DEFAULT_CAPTURE_REGION.split(','))
        return (x, y, w, h)
