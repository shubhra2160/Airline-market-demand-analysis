import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from collections import defaultdict
import logging

from ..models.flight_models import Flight, DemandMetric, Route, Insight
from ..database import SessionLocal

logger = logging.getLogger(__name__)

class DataProcessingService:
    """Service for processing flight data and calculating demand metrics"""
    
    def __init__(self):
        self.seasonal_periods = {
            "summer": [12, 1, 2],
            "autumn": [3, 4, 5],
            "winter": [6, 7, 8],
            "spring": [9, 10, 11]
        }
        
        self.holiday_periods = [
            # Christmas/New Year
            (datetime(2024, 12, 20), datetime(2024, 1, 10)),
            # Easter (approximate)
            (datetime(2024, 3, 25), datetime(2024, 4, 5)),
            # School holidays (approximate)
            (datetime(2024, 6, 20), datetime(2024, 7, 20)),
            (datetime(2024, 9, 15), datetime(2024, 10, 5)),
        ]
    
    def clean_flight_data(self, flight_data: Dict) -> Dict:
        """Clean and validate flight data"""
        try:
            # Remove null/empty values
            cleaned_data = {k: v for k, v in flight_data.items() if v is not None and v != ""}
            
            # Validate required fields
            required_fields = ["origin", "destination", "departure_date", "price"]
            for field in required_fields:
                if field not in cleaned_data:
                    logger.warning(f"Missing required field: {field}")
                    return None
            
            # Clean and validate price
            if "price" in cleaned_data:
                try:
                    cleaned_data["price"] = float(cleaned_data["price"])
                    if cleaned_data["price"] <= 0:
                        logger.warning("Invalid price value")
                        return None
                except (ValueError, TypeError):
                    logger.warning("Invalid price format")
                    return None
            
            # Clean departure date
            if "departure_date" in cleaned_data:
                try:
                    if isinstance(cleaned_data["departure_date"], str):
                        cleaned_data["departure_date"] = datetime.fromisoformat(
                            cleaned_data["departure_date"].replace("Z", "+00:00")
                        )
                except (ValueError, TypeError):
                    logger.warning("Invalid departure date format")
                    return None
            
            # Clean return date if present
            if "return_date" in cleaned_data and cleaned_data["return_date"]:
                try:
                    if isinstance(cleaned_data["return_date"], str):
                        cleaned_data["return_date"] = datetime.fromisoformat(
                            cleaned_data["return_date"].replace("Z", "+00:00")
                        )
                except (ValueError, TypeError):
                    cleaned_data["return_date"] = None
            
            # Validate airport codes
            if len(cleaned_data["origin"]) != 3 or len(cleaned_data["destination"]) != 3:
                logger.warning("Invalid airport codes")
                return None
            
            # Set defaults
            cleaned_data.setdefault("currency", "AUD")
            cleaned_data.setdefault("availability", 0)
            cleaned_data.setdefault("data_source", "amadeus")
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning flight data: {str(e)}")
            return None
    
    def calculate_demand_score(self, flight_data: Dict, historical_data: List[Dict] = None) -> float:
        """Calculate demand score based on various factors"""
        try:
            score = 50.0  # Base score
            
            # Price factor (lower price = higher demand potential)
            price = flight_data.get("price", 0)
            if price > 0:
                # Normalize price (assuming $100-2000 range)
                price_factor = max(0, min(100, 100 - ((price - 100) / 19)))
                score += (price_factor - 50) * 0.3
            
            # Availability factor (lower availability = higher demand)
            availability = flight_data.get("availability", 0)
            if availability > 0:
                # Lower availability suggests higher demand
                availability_factor = max(0, min(100, 100 - (availability / 2)))
                score += (availability_factor - 50) * 0.2
            
            # Route popularity factor
            route_score = self.calculate_route_popularity(
                flight_data.get("origin", ""),
                flight_data.get("destination", "")
            )
            score += (route_score - 50) * 0.2
            
            # Seasonal factor
            departure_date = flight_data.get("departure_date")
            if departure_date:
                seasonal_score = self.calculate_seasonal_score(departure_date)
                score += (seasonal_score - 50) * 0.15
            
            # Holiday factor
            if departure_date and self.is_holiday_period(departure_date):
                score += 10
            
            # Weekend factor
            if departure_date and departure_date.weekday() >= 5:  # Saturday/Sunday
                score += 5
            
            # Ensure score is between 0-100
            score = max(0, min(100, score))
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating demand score: {str(e)}")
            return 50.0
    
    def calculate_route_popularity(self, origin: str, destination: str) -> float:
        """Calculate route popularity score"""
        try:
            # Major Australian routes (higher popularity)
            major_routes = [
                ("SYD", "MEL"), ("MEL", "SYD"),
                ("SYD", "BNE"), ("BNE", "SYD"),
                ("SYD", "PER"), ("PER", "SYD"),
                ("MEL", "BNE"), ("BNE", "MEL"),
                ("MEL", "PER"), ("PER", "MEL"),
                ("BNE", "PER"), ("PER", "BNE"),
            ]
            
            # International routes from major hubs
            international_routes = [
                ("SYD", "LAX"), ("MEL", "LAX"),
                ("SYD", "LHR"), ("MEL", "LHR"),
                ("SYD", "NRT"), ("MEL", "NRT"),
                ("SYD", "SIN"), ("MEL", "SIN"),
                ("BNE", "LAX"), ("BNE", "NRT"),
            ]
            
            route = (origin, destination)
            
            if route in major_routes:
                return 80.0
            elif route in international_routes:
                return 70.0
            elif origin in ["SYD", "MEL", "BNE"] or destination in ["SYD", "MEL", "BNE"]:
                return 60.0
            else:
                return 40.0
                
        except Exception as e:
            logger.error(f"Error calculating route popularity: {str(e)}")
            return 50.0
    
    def calculate_seasonal_score(self, departure_date: datetime) -> float:
        """Calculate seasonal demand score"""
        try:
            month = departure_date.month
            
            # Australian seasons (opposite to Northern Hemisphere)
            if month in [12, 1, 2]:  # Summer
                return 85.0  # High demand for summer holidays
            elif month in [3, 4, 5]:  # Autumn
                return 60.0  # Moderate demand
            elif month in [6, 7, 8]:  # Winter
                return 70.0  # Winter school holidays
            elif month in [9, 10, 11]:  # Spring
                return 65.0  # Spring break periods
            
            return 50.0
            
        except Exception as e:
            logger.error(f"Error calculating seasonal score: {str(e)}")
            return 50.0
    
    def is_holiday_period(self, date: datetime) -> bool:
        """Check if date falls within holiday periods"""
        try:
            for start, end in self.holiday_periods:
                if start <= date <= end:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking holiday period: {str(e)}")
            return False
    
    def calculate_price_trend(self, current_price: float, historical_prices: List[float]) -> str:
        """Calculate price trend based on historical data"""
        try:
            if not historical_prices or len(historical_prices) < 2:
                return "stable"
            
            # Calculate average of recent prices
            recent_avg = np.mean(historical_prices[-5:])  # Last 5 data points
            older_avg = np.mean(historical_prices[:-5]) if len(historical_prices) > 5 else recent_avg
            
            # Calculate percentage change
            if older_avg > 0:
                change_percent = ((recent_avg - older_avg) / older_avg) * 100
                
                if change_percent > 10:
                    return "increasing"
                elif change_percent < -10:
                    return "decreasing"
                else:
                    return "stable"
            
            return "stable"
            
        except Exception as e:
            logger.error(f"Error calculating price trend: {str(e)}")
            return "stable"
    
    def process_flight_batch(self, flight_data_list: List[Dict]) -> List[Dict]:
        """Process a batch of flight data"""
        processed_flights = []
        
        for flight_data in flight_data_list:
            # Clean the data
            cleaned_data = self.clean_flight_data(flight_data)
            if not cleaned_data:
                continue
            
            # Calculate demand score
            demand_score = self.calculate_demand_score(cleaned_data)
            
            # Add calculated fields
            cleaned_data["demand_score"] = demand_score
            cleaned_data["season"] = self.get_season(cleaned_data.get("departure_date"))
            cleaned_data["is_holiday_period"] = self.is_holiday_period(cleaned_data.get("departure_date"))
            cleaned_data["is_weekend"] = cleaned_data.get("departure_date").weekday() >= 5
            
            processed_flights.append(cleaned_data)
        
        return processed_flights
    
    def get_season(self, date: datetime) -> str:
        """Get season for a given date"""
        try:
            if not date:
                return "unknown"
            
            month = date.month
            for season, months in self.seasonal_periods.items():
                if month in months:
                    return season
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error getting season: {str(e)}")
            return "unknown"
    
    def aggregate_route_data(self, db: Session) -> List[Dict]:
        """Aggregate route data for analysis"""
        try:
            # Query all flights
            flights = db.query(Flight).all()
            
            # Group by route
            route_data = defaultdict(lambda: {
                "total_flights": 0,
                "prices": [],
                "demand_scores": [],
                "search_count": 0,
                "booking_count": 0
            })
            
            for flight in flights:
                route_key = f"{flight.origin}-{flight.destination}"
                route_info = route_data[route_key]
                
                route_info["total_flights"] += 1
                if flight.price:
                    route_info["prices"].append(flight.price)
                
                # Get demand metrics
                for metric in flight.demand_metrics:
                    if metric.demand_score:
                        route_info["demand_scores"].append(metric.demand_score)
                    if metric.search_volume:
                        route_info["search_count"] += metric.search_volume
                    if metric.booking_volume:
                        route_info["booking_count"] += metric.booking_volume
            
            # Calculate aggregated metrics
            aggregated_routes = []
            for route_key, data in route_data.items():
                origin, destination = route_key.split("-")
                
                route_metrics = {
                    "origin": origin,
                    "destination": destination,
                    "total_flights": data["total_flights"],
                    "average_price": np.mean(data["prices"]) if data["prices"] else 0,
                    "price_variance": np.var(data["prices"]) if data["prices"] else 0,
                    "average_demand_score": np.mean(data["demand_scores"]) if data["demand_scores"] else 0,
                    "search_frequency": data["search_count"],
                    "booking_frequency": data["booking_count"],
                    "route_popularity_score": self.calculate_route_popularity(origin, destination)
                }
                
                aggregated_routes.append(route_metrics)
            
            return aggregated_routes
            
        except Exception as e:
            logger.error(f"Error aggregating route data: {str(e)}")
            return []
    
    def generate_insights_data(self, db: Session) -> Dict:
        """Generate data for insights"""
        try:
            # Get all flights
            flights = db.query(Flight).all()
            
            # Convert to DataFrame for analysis
            flight_data = []
            for flight in flights:
                flight_dict = {
                    "origin": flight.origin,
                    "destination": flight.destination,
                    "departure_date": flight.departure_date,
                    "price": flight.price,
                    "airline": flight.airline,
                    "is_domestic": flight.is_domestic,
                    "created_at": flight.created_at
                }
                
                # Add demand metrics
                for metric in flight.demand_metrics:
                    flight_dict.update({
                        "demand_score": metric.demand_score,
                        "season": metric.season,
                        "is_holiday_period": metric.is_holiday_period,
                        "is_weekend": metric.is_weekend,
                        "price_trend": metric.price_trend
                    })
                
                flight_data.append(flight_dict)
            
            if not flight_data:
                return {}
            
            df = pd.DataFrame(flight_data)
            
            # Generate insights
            insights = {
                "total_flights": len(df),
                "domestic_flights": len(df[df["is_domestic"] == True]),
                "international_flights": len(df[df["is_domestic"] == False]),
                "average_price": df["price"].mean() if not df["price"].isna().all() else 0,
                "price_range": {
                    "min": df["price"].min() if not df["price"].isna().all() else 0,
                    "max": df["price"].max() if not df["price"].isna().all() else 0
                },
                "popular_routes": self.get_popular_routes(df),
                "price_trends": self.get_price_trends(df),
                "seasonal_patterns": self.get_seasonal_patterns(df),
                "demand_patterns": self.get_demand_patterns(df)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights data: {str(e)}")
            return {}
    
    def get_popular_routes(self, df: pd.DataFrame) -> List[Dict]:
        """Get popular routes from flight data"""
        try:
            route_counts = df.groupby(["origin", "destination"]).size().reset_index(name="count")
            route_counts = route_counts.sort_values("count", ascending=False).head(10)
            
            popular_routes = []
            for _, row in route_counts.iterrows():
                popular_routes.append({
                    "origin": row["origin"],
                    "destination": row["destination"],
                    "flight_count": row["count"]
                })
            
            return popular_routes
            
        except Exception as e:
            logger.error(f"Error getting popular routes: {str(e)}")
            return []
    
    def get_price_trends(self, df: pd.DataFrame) -> Dict:
        """Get price trends from flight data"""
        try:
            if df.empty or "price_trend" not in df.columns:
                return {}
            
            trend_counts = df["price_trend"].value_counts().to_dict()
            
            return {
                "increasing": trend_counts.get("increasing", 0),
                "decreasing": trend_counts.get("decreasing", 0),
                "stable": trend_counts.get("stable", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting price trends: {str(e)}")
            return {}
    
    def get_seasonal_patterns(self, df: pd.DataFrame) -> Dict:
        """Get seasonal patterns from flight data"""
        try:
            if df.empty or "season" not in df.columns:
                return {}
            
            seasonal_counts = df["season"].value_counts().to_dict()
            
            return {
                "summer": seasonal_counts.get("summer", 0),
                "autumn": seasonal_counts.get("autumn", 0),
                "winter": seasonal_counts.get("winter", 0),
                "spring": seasonal_counts.get("spring", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting seasonal patterns: {str(e)}")
            return {}
    
    def get_demand_patterns(self, df: pd.DataFrame) -> Dict:
        """Get demand patterns from flight data"""
        try:
            if df.empty or "demand_score" not in df.columns:
                return {}
            
            # Calculate demand categories
            high_demand = len(df[df["demand_score"] >= 70])
            medium_demand = len(df[(df["demand_score"] >= 40) & (df["demand_score"] < 70)])
            low_demand = len(df[df["demand_score"] < 40])
            
            return {
                "high_demand": high_demand,
                "medium_demand": medium_demand,
                "low_demand": low_demand,
                "average_demand_score": df["demand_score"].mean()
            }
            
        except Exception as e:
            logger.error(f"Error getting demand patterns: {str(e)}")
            return {}

# Create service instance
data_processing_service = DataProcessingService() 