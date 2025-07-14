from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Flight(Base):
    """Flight data model"""
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic flight information
    origin = Column(String(3), nullable=False, index=True)  # Airport code
    destination = Column(String(3), nullable=False, index=True)  # Airport code
    departure_date = Column(DateTime, nullable=False, index=True)
    return_date = Column(DateTime, nullable=True)
    
    # Flight details
    airline = Column(String(100), nullable=True)
    flight_number = Column(String(20), nullable=True)
    aircraft_type = Column(String(50), nullable=True)
    
    # Pricing information
    price = Column(Float, nullable=True)
    currency = Column(String(3), default="AUD")
    price_class = Column(String(20), nullable=True)  # Economy, Business, First
    
    # Market demand indicators
    availability = Column(Integer, nullable=True)  # Number of seats available
    booking_class = Column(String(1), nullable=True)  # Y, B, M, etc.
    
    # Metadata
    is_domestic = Column(Boolean, default=True)
    data_source = Column(String(50), default="amadeus")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    demand_metrics = relationship("DemandMetric", back_populates="flight")

class DemandMetric(Base):
    """Market demand metrics model"""
    __tablename__ = "demand_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    
    # Demand indicators
    search_volume = Column(Integer, nullable=True)
    booking_volume = Column(Integer, nullable=True)
    price_trend = Column(String(20), nullable=True)  # increasing, decreasing, stable
    
    # Seasonal patterns
    season = Column(String(20), nullable=True)  # summer, winter, spring, fall
    is_holiday_period = Column(Boolean, default=False)
    is_weekend = Column(Boolean, default=False)
    
    # Demand score (calculated)
    demand_score = Column(Float, nullable=True)  # 0-100 scale
    
    # Metadata
    analysis_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    flight = relationship("Flight", back_populates="demand_metrics")

class Route(Base):
    """Route popularity and metrics model"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Route information
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    
    # Route metrics
    total_flights = Column(Integer, default=0)
    average_price = Column(Float, nullable=True)
    price_variance = Column(Float, nullable=True)
    
    # Popularity metrics
    search_frequency = Column(Integer, default=0)
    booking_frequency = Column(Integer, default=0)
    route_popularity_score = Column(Float, nullable=True)
    
    # Route characteristics
    is_domestic = Column(Boolean, default=True)
    distance_km = Column(Float, nullable=True)
    flight_duration_minutes = Column(Integer, nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

class Insight(Base):
    """AI-generated insights model"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Insight content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    insight_type = Column(String(50), nullable=False)  # trend, recommendation, alert
    
    # Insight metadata
    confidence_score = Column(Float, nullable=True)  # 0-1 scale
    data_points_used = Column(Integer, nullable=True)
    
    # Categorization
    category = Column(String(50), nullable=True)  # pricing, demand, routes, seasonal
    priority = Column(String(20), default="medium")  # high, medium, low
    
    # Validity
    is_active = Column(Boolean, default=True)
    valid_until = Column(DateTime, nullable=True)
    
    # Metadata
    generated_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

class ApiUsage(Base):
    """API usage tracking model"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # API details
    api_name = Column(String(50), nullable=False)  # amadeus, openai
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    
    # Usage tracking
    requests_count = Column(Integer, default=1)
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Rate limiting
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset = Column(DateTime, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now()) 