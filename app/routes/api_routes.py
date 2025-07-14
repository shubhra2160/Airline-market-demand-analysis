from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

from ..database import get_db
from ..models.flight_models import Flight, DemandMetric, Route, Insight
from ..services.data_processing import data_processing_service
from ..services.openai_service import openai_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary statistics for dashboard"""
    try:
        # Get basic counts
        total_flights = db.query(Flight).count()
        domestic_flights = db.query(Flight).filter(Flight.is_domestic == True).count()
        international_flights = db.query(Flight).filter(Flight.is_domestic == False).count()
        
        # Get price statistics
        price_stats = db.query(
            func.avg(Flight.price).label('avg_price'),
            func.min(Flight.price).label('min_price'),
            func.max(Flight.price).label('max_price')
        ).filter(Flight.price.isnot(None)).first()
        
        # Get recent flights (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_flights = db.query(Flight).filter(
            Flight.created_at >= week_ago
        ).count()
        
        # Get top routes
        top_routes = db.query(
            Flight.origin,
            Flight.destination,
            func.count(Flight.id).label('flight_count')
        ).group_by(Flight.origin, Flight.destination).order_by(
            func.count(Flight.id).desc()
        ).limit(5).all()
        
        # Get demand distribution
        demand_stats = db.query(
            func.avg(DemandMetric.demand_score).label('avg_demand'),
            func.count(DemandMetric.id).label('total_metrics')
        ).first()
        
        return {
            "total_flights": total_flights,
            "domestic_flights": domestic_flights,
            "international_flights": international_flights,
            "price_stats": {
                "average": float(price_stats.avg_price) if price_stats.avg_price else 0,
                "minimum": float(price_stats.min_price) if price_stats.min_price else 0,
                "maximum": float(price_stats.max_price) if price_stats.max_price else 0
            },
            "recent_activity": {
                "flights_last_week": recent_flights
            },
            "top_routes": [
                {
                    "origin": route.origin,
                    "destination": route.destination,
                    "flight_count": route.flight_count
                } for route in top_routes
            ],
            "demand_stats": {
                "average_demand_score": float(demand_stats.avg_demand) if demand_stats.avg_demand else 0,
                "total_metrics": demand_stats.total_metrics
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/price-trends")
async def get_price_trends(
    days: int = 30,
    route: Optional[str] = None,
    is_domestic: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get price trend data for charts"""
    try:
        # Calculate date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Base query - use departure_date instead of created_at
        query = db.query(
            func.date(Flight.departure_date).label('date'),
            func.avg(Flight.price).label('avg_price'),
            func.count(Flight.id).label('flight_count')
        ).filter(
            Flight.departure_date >= start_date,
            Flight.price.isnot(None)
        )
        
        # Apply route filter if provided
        if route:
            origin, destination = route.split('-') if '-' in route else (route, None)
            query = query.filter(Flight.origin == origin.upper())
            if destination:
                query = query.filter(Flight.destination == destination.upper())
        
        # Apply domestic filter if provided
        if is_domestic is not None:
            query = query.filter(Flight.is_domestic == is_domestic)
        
        # Group by date and get results
        results = query.group_by(func.date(Flight.departure_date)).order_by(
            func.date(Flight.departure_date)
        ).all()
        
        # Format data for charts
        chart_data = {
            "dates": [str(result.date) for result in results],
            "prices": [float(result.avg_price) for result in results],
            "flight_counts": [result.flight_count for result in results]
        }
        
        return {
            "chart_data": chart_data,
            "period": f"{days} days",
            "route_filter": route,
            "total_points": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting price trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/demand-heatmap")
async def get_demand_heatmap(
    days: int = 30,
    is_domestic: Optional[bool] = None,
    route: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get demand heatmap data"""
    try:
        # Calculate date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Get demand scores by route
        query = db.query(
            Flight.origin,
            Flight.destination,
            func.avg(DemandMetric.demand_score).label('avg_demand'),
            func.count(DemandMetric.id).label('metric_count')
        ).join(DemandMetric).filter(
            Flight.departure_date >= start_date
        )
        
        # Apply domestic filter if provided
        if is_domestic is not None:
            query = query.filter(Flight.is_domestic == is_domestic)
        
        # Apply specific route filter if provided
        if route:
            origin, destination = route.split('-') if '-' in route else (route, None)
            query = query.filter(Flight.origin == origin.upper())
            if destination:
                query = query.filter(Flight.destination == destination.upper())
        
        demand_data = query.group_by(
            Flight.origin, Flight.destination
        ).having(func.count(DemandMetric.id) > 0).all()
        
        # Format for heatmap
        heatmap_data = []
        for item in demand_data:
            heatmap_data.append({
                "origin": item.origin,
                "destination": item.destination,
                "demand_score": float(item.avg_demand),
                "metric_count": item.metric_count
            })
        
        # Get unique origins and destinations for axes
        origins = list(set([item["origin"] for item in heatmap_data]))
        destinations = list(set([item["destination"] for item in heatmap_data]))
        
        return {
            "heatmap_data": heatmap_data,
            "origins": origins,
            "destinations": destinations,
            "total_routes": len(heatmap_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting demand heatmap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/route-popularity")
async def get_route_popularity(
    limit: int = 20,
    is_domestic: Optional[bool] = None,
    days: int = 30,
    route: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get route popularity data for bar charts"""
    try:
        # Calculate date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Build query
        query = db.query(
            Flight.origin,
            Flight.destination,
            func.count(Flight.id).label('flight_count'),
            func.avg(Flight.price).label('avg_price'),
            func.avg(DemandMetric.demand_score).label('avg_demand')
        ).outerjoin(DemandMetric).filter(
            Flight.departure_date >= start_date
        )
        
        # Apply domestic filter if provided
        if is_domestic is not None:
            query = query.filter(Flight.is_domestic == is_domestic)
        
        # Apply specific route filter if provided
        if route:
            origin, destination = route.split('-') if '-' in route else (route, None)
            query = query.filter(Flight.origin == origin.upper())
            if destination:
                query = query.filter(Flight.destination == destination.upper())
        
        # Group and order
        results = query.group_by(
            Flight.origin, Flight.destination
        ).order_by(
            func.count(Flight.id).desc()
        ).limit(limit).all()
        
        # Format data
        chart_data = []
        for result in results:
            chart_data.append({
                "route": f"{result.origin} → {result.destination}",
                "flight_count": result.flight_count,
                "avg_price": float(result.avg_price) if result.avg_price else 0,
                "avg_demand": float(result.avg_demand) if result.avg_demand else 0
            })
        
        return {
            "chart_data": chart_data,
            "filter": {
                "limit": limit,
                "is_domestic": is_domestic,
                "days": days,
                "route": route
            },
            "total_routes": len(chart_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting route popularity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/seasonal-patterns")
async def get_seasonal_patterns(
    days: int = 30,
    is_domestic: Optional[bool] = None,
    route: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get seasonal demand patterns"""
    try:
        # Calculate date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Get seasonal data
        query = db.query(
            DemandMetric.season,
            func.avg(DemandMetric.demand_score).label('avg_demand'),
            func.count(DemandMetric.id).label('metric_count')
        ).join(Flight).filter(
            DemandMetric.season.isnot(None),
            Flight.departure_date >= start_date
        )
        
        # Apply domestic filter if provided
        if is_domestic is not None:
            query = query.filter(Flight.is_domestic == is_domestic)
        
        # Apply specific route filter if provided
        if route:
            origin, destination = route.split('-') if '-' in route else (route, None)
            query = query.filter(Flight.origin == origin.upper())
            if destination:
                query = query.filter(Flight.destination == destination.upper())
        
        seasonal_data = query.group_by(
            DemandMetric.season
        ).all()
        
        # Format data for chart
        chart_data = []
        for item in seasonal_data:
            chart_data.append({
                "season": item.season,
                "flight_count": item.metric_count,
                "avg_demand": float(item.avg_demand)
            })
        
        # Get holiday vs non-holiday comparison
        holiday_query = db.query(
            DemandMetric.is_holiday_period,
            func.avg(DemandMetric.demand_score).label('avg_demand'),
            func.count(DemandMetric.id).label('metric_count')
        ).join(Flight).filter(
            Flight.departure_date >= start_date
        )
        
        # Apply same filters as seasonal data
        if is_domestic is not None:
            holiday_query = holiday_query.filter(Flight.is_domestic == is_domestic)
        
        if route:
            origin, destination = route.split('-') if '-' in route else (route, None)
            holiday_query = holiday_query.filter(Flight.origin == origin.upper())
            if destination:
                holiday_query = holiday_query.filter(Flight.destination == destination.upper())
        
        holiday_data = holiday_query.group_by(DemandMetric.is_holiday_period).all()
        
        holiday_comparison = {
            "holiday": 0,
            "non_holiday": 0
        }
        
        for item in holiday_data:
            if item.is_holiday_period:
                holiday_comparison["holiday"] = float(item.avg_demand)
            else:
                holiday_comparison["non_holiday"] = float(item.avg_demand)
        
        return {
            "chart_data": chart_data,
            "holiday_comparison": holiday_comparison,
            "filter": {
                "days": days,
                "is_domestic": is_domestic,
                "route": route
            },
            "total_metrics": sum(item["flight_count"] for item in chart_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting seasonal patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights(
    limit: int = 10,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI-generated insights"""
    try:
        # Query insights
        query = db.query(Insight).filter(Insight.is_active == True)
        
        if category:
            query = query.filter(Insight.category == category)
        
        insights = query.order_by(Insight.generated_at.desc()).limit(limit).all()
        
        # Format insights
        insights_data = []
        for insight in insights:
            insights_data.append({
                "id": insight.id,
                "title": insight.title,
                "content": insight.content,
                "type": insight.insight_type,
                "category": insight.category,
                "confidence_score": insight.confidence_score,
                "priority": insight.priority,
                "generated_at": insight.generated_at.isoformat() if insight.generated_at else None
            })
        
        return {
            "insights": insights_data,
            "total": len(insights_data),
            "filter": {
                "limit": limit,
                "category": category
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/generate")
async def generate_insights(db: Session = Depends(get_db)):
    """Generate new insights from current data"""
    try:
        # Get current data for analysis
        insights_data = data_processing_service.generate_insights_data(db)
        
        if not insights_data:
            raise HTTPException(status_code=400, detail="No data available for analysis")
        
        # Generate AI insights
        ai_insights = await openai_service.generate_market_insights(insights_data)
        
        # Save insights to database
        saved_insights = []
        if 'structured_insights' in ai_insights:
            for insight_data in ai_insights['structured_insights']:
                insight = Insight(
                    title=insight_data.get('title', 'Generated Insight'),
                    content=insight_data.get('content', ''),
                    insight_type=insight_data.get('type', 'insight'),
                    category='market_analysis',
                    confidence_score=ai_insights.get('confidence_score', 0.5),
                    priority='medium'
                )
                
                db.add(insight)
                saved_insights.append(insight)
        
        db.commit()
        
        return {
            "message": "Insights generated successfully",
            "insights_count": len(saved_insights),
            "confidence_score": ai_insights.get('confidence_score', 0.5),
            "generated_at": ai_insights.get('generated_at')
        }
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/airports")
async def get_airports(db: Session = Depends(get_db)):
    """Get list of airports for filtering"""
    try:
        # Get unique origins and destinations
        origins = db.query(Flight.origin).distinct().all()
        destinations = db.query(Flight.destination).distinct().all()
        
        # Combine and deduplicate
        all_airports = set()
        for origin in origins:
            all_airports.add(origin[0])
        for destination in destinations:
            all_airports.add(destination[0])
        
        airports = sorted(list(all_airports))
        
        return {
            "airports": airports,
            "total": len(airports)
        }
        
    except Exception as e:
        logger.error(f"Error getting airports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/airlines")
async def get_airlines(db: Session = Depends(get_db)):
    """Get list of airlines for filtering"""
    try:
        airlines = db.query(Flight.airline).filter(
            Flight.airline.isnot(None)
        ).distinct().all()
        
        airline_list = sorted([airline[0] for airline in airlines if airline[0]])
        
        return {
            "airlines": airline_list,
            "total": len(airline_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting airlines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 