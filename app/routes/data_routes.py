from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models.flight_models import Flight, DemandMetric, Route
from ..services.amadeus_service import amadeus_service
from ..services.data_processing import data_processing_service
from ..services.openai_service import openai_service
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/fetch-flights")
async def fetch_flights(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Fetch flight data from Amadeus API"""
    try:
        # Start background task to fetch flights
        background_tasks.add_task(fetch_and_process_flights, db)
        
        return {
            "message": "Flight data fetching started",
            "status": "processing",
            "estimated_completion": "5-10 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting flight fetch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flights")
async def get_flights(
    limit: int = 100,
    offset: int = 0,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    is_domestic: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get flights with filtering options"""
    try:
        query = db.query(Flight)
        
        # Apply filters
        if origin:
            query = query.filter(Flight.origin == origin.upper())
        if destination:
            query = query.filter(Flight.destination == destination.upper())
        if is_domestic is not None:
            query = query.filter(Flight.is_domestic == is_domestic)
        
        # Apply pagination
        flights = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        flight_data = []
        for flight in flights:
            flight_dict = {
                "id": flight.id,
                "origin": flight.origin,
                "destination": flight.destination,
                "departure_date": flight.departure_date.isoformat() if flight.departure_date else None,
                "return_date": flight.return_date.isoformat() if flight.return_date else None,
                "airline": flight.airline,
                "flight_number": flight.flight_number,
                "price": flight.price,
                "currency": flight.currency,
                "is_domestic": flight.is_domestic,
                "created_at": flight.created_at.isoformat() if flight.created_at else None
            }
            flight_data.append(flight_dict)
        
        return {
            "flights": flight_data,
            "total": len(flight_data),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting flights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes")
async def get_routes(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get route analytics"""
    try:
        routes = db.query(Route).offset(offset).limit(limit).all()
        
        route_data = []
        for route in routes:
            route_dict = {
                "id": route.id,
                "origin": route.origin,
                "destination": route.destination,
                "total_flights": route.total_flights,
                "average_price": route.average_price,
                "route_popularity_score": route.route_popularity_score,
                "is_domestic": route.is_domestic,
                "last_updated": route.last_updated.isoformat() if route.last_updated else None
            }
            route_data.append(route_dict)
        
        return {
            "routes": route_data,
            "total": len(route_data),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting routes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-demand")
async def analyze_demand(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze demand patterns and generate insights"""
    try:
        # Start background task for demand analysis
        background_tasks.add_task(analyze_demand_patterns, db)
        
        return {
            "message": "Demand analysis started",
            "status": "processing",
            "estimated_completion": "2-3 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting demand analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demand-metrics")
async def get_demand_metrics(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get demand metrics data"""
    try:
        metrics = db.query(DemandMetric).offset(offset).limit(limit).all()
        
        metrics_data = []
        for metric in metrics:
            metric_dict = {
                "id": metric.id,
                "flight_id": metric.flight_id,
                "demand_score": metric.demand_score,
                "season": metric.season,
                "is_holiday_period": metric.is_holiday_period,
                "is_weekend": metric.is_weekend,
                "price_trend": metric.price_trend,
                "analysis_date": metric.analysis_date.isoformat() if metric.analysis_date else None
            }
            metrics_data.append(metric_dict)
        
        return {
            "metrics": metrics_data,
            "total": len(metrics_data),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting demand metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-flights")
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1
):
    """Search for flights using Amadeus API"""
    try:
        # Validate inputs
        if len(origin) != 3 or len(destination) != 3:
            raise HTTPException(status_code=400, detail="Airport codes must be 3 characters")
        
        # Search flights
        flights = await amadeus_service.search_flights(
            origin=origin.upper(),
            destination=destination.upper(),
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            max_results=50
        )
        
        if not flights:
            return {
                "flights": [],
                "message": "No flights found or API error",
                "total": 0
            }
        
        # Parse flight data
        parsed_flights = []
        for flight in flights:
            parsed_flight = amadeus_service.parse_flight_data(flight)
            if parsed_flight:
                parsed_flights.append(parsed_flight)
        
        return {
            "flights": parsed_flights,
            "total": len(parsed_flights),
            "search_params": {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date,
                "return_date": return_date,
                "adults": adults
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching flights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_and_process_flights(db: Session):
    """Background task to fetch and process flights"""
    try:
        logger.info("Starting flight data collection...")
        
        # Fetch domestic flights
        domestic_flights = await amadeus_service.get_domestic_flights()
        logger.info(f"Fetched {len(domestic_flights)} domestic flights")
        
        # Fetch international flights
        international_flights = await amadeus_service.get_international_flights()
        logger.info(f"Fetched {len(international_flights)} international flights")
        
        # Combine all flights
        all_flights = domestic_flights + international_flights
        
        # Process flights
        processed_flights = data_processing_service.process_flight_batch(all_flights)
        logger.info(f"Processed {len(processed_flights)} flights")
        
        # Save to database
        for flight_data in processed_flights:
            try:
                # Filter flights to only include configured origins and destinations
                origin = flight_data.get("origin")
                destination = flight_data.get("destination")
                
                # Check if this flight matches our configured routes
                is_valid_domestic = (origin in settings.AUSTRALIAN_CITIES and 
                                   destination in settings.AUSTRALIAN_CITIES and 
                                   origin != destination)
                is_valid_international = (origin in settings.AUSTRALIAN_CITIES and 
                                        destination in settings.INTERNATIONAL_DESTINATIONS)
                
                if not (is_valid_domestic or is_valid_international):
                    continue  # Skip this flight as it's not in our configured routes
                
                # Correctly determine if flight is domestic or international
                flight_is_domestic = is_valid_domestic  # True if both origin and destination are Australian cities
                
                # Create flight record
                flight = Flight(
                    origin=origin,
                    destination=destination,
                    departure_date=flight_data.get("departure_date"),
                    return_date=flight_data.get("return_date"),
                    airline=flight_data.get("airline"),
                    flight_number=flight_data.get("flight_number"),
                    aircraft_type=flight_data.get("aircraft_type"),
                    price=flight_data.get("price"),
                    currency=flight_data.get("currency"),
                    price_class=flight_data.get("price_class"),
                    availability=flight_data.get("availability"),
                    booking_class=flight_data.get("booking_class"),
                    is_domestic=flight_is_domestic,
                    data_source="amadeus"
                )
                
                db.add(flight)
                db.flush()  # Get the ID
                
                # Create demand metric
                demand_metric = DemandMetric(
                    flight_id=flight.id,
                    demand_score=flight_data.get("demand_score"),
                    season=flight_data.get("season"),
                    is_holiday_period=flight_data.get("is_holiday_period"),
                    is_weekend=flight_data.get("is_weekend"),
                    price_trend="stable"  # Default value
                )
                
                db.add(demand_metric)
                
            except Exception as e:
                logger.error(f"Error saving flight data: {str(e)}")
                continue
        
        db.commit()
        logger.info("Flight data collection completed successfully")
        
    except Exception as e:
        logger.error(f"Error in flight collection background task: {str(e)}")
        db.rollback()

async def analyze_demand_patterns(db: Session):
    """Background task to analyze demand patterns"""
    try:
        logger.info("Starting demand pattern analysis...")
        
        # Generate insights data
        insights_data = data_processing_service.generate_insights_data(db)
        
        # Generate AI insights
        ai_insights = await openai_service.generate_market_insights(insights_data)
        
        # Get route data for analysis
        route_data = data_processing_service.aggregate_route_data(db)
        
        # Generate route analysis
        route_analysis = await openai_service.analyze_route_performance(route_data)
        
        # Save insights to database would go here
        # For now, we'll just log them
        logger.info("Demand analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Error in demand analysis background task: {str(e)}") 