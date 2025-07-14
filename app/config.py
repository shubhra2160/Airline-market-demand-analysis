import os
from typing import ClassVar, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./airline_demand.db"
    
    # Amadeus API
    AMADEUS_API_KEY: str = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET: str = os.getenv("AMADEUS_API_SECRET", "")
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # App settings
    APP_NAME: str = "Airline Booking Market Demand Analyzer"
    DEBUG: bool = True
    
    # Rate limiting
    AMADEUS_RATE_LIMIT: int = 100 
    OPENAI_RATE_LIMIT: int = 60
    
    # Australian cities for domestic flights (top 3 major cities)
    AUSTRALIAN_CITIES: ClassVar[List[str]] = [
        "SYD",  # Sydney
        "MEL",  # Melbourne 
        "BNE"   # Brisbane
    ]
    
    # International destinations from Australia (top 3 major destinations)
    INTERNATIONAL_DESTINATIONS: ClassVar[List[str]] = [
        "LAX",  # Los Angeles
        "LHR",  # London Heathrow
        "SIN"   # Singapore
    ]
    
    model_config = {"env_file": ".env"}

# Create settings instance
settings = Settings() 