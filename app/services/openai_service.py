import openai
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for generating insights using OpenAI API"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
    
    async def generate_market_insights(self, data: Dict) -> Dict:
        """Generate market insights from flight data"""
        try:
            # Prepare prompt with data
            prompt = self._create_insights_prompt(data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert aviation market analyst. Provide clear, actionable insights about airline booking trends and market demand."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            insight_text = response.choices[0].message.content
            
            # Parse and structure the insights
            insights = self._parse_insights(insight_text)
            
            return {
                "raw_insight": insight_text,
                "structured_insights": insights,
                "generated_at": datetime.now().isoformat(),
                "confidence_score": self._calculate_confidence(data)
            }
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def analyze_price_trends(self, route_data: List[Dict]) -> Dict:
        """Analyze price trends for specific routes"""
        try:
            prompt = self._create_price_trend_prompt(route_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pricing analyst specializing in airline industry. Analyze price trends and provide recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.6
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "analysis": analysis_text,
                "recommendations": self._extract_recommendations(analysis_text),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price trends: {str(e)}")
            return {"error": str(e)}
    
    async def generate_demand_forecast(self, historical_data: Dict) -> Dict:
        """Generate demand forecasts based on historical data"""
        try:
            prompt = self._create_forecast_prompt(historical_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a demand forecasting specialist for the aviation industry. Provide realistic forecasts with confidence intervals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5
            )
            
            forecast_text = response.choices[0].message.content
            
            return {
                "forecast": forecast_text,
                "key_factors": self._extract_key_factors(forecast_text),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating demand forecast: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_route_performance(self, route_metrics: List[Dict]) -> Dict:
        """Analyze route performance and identify opportunities"""
        try:
            prompt = self._create_route_analysis_prompt(route_metrics)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a route performance analyst. Identify high-performing routes and growth opportunities."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.6
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "analysis": analysis_text,
                "top_routes": self._extract_top_routes(analysis_text),
                "opportunities": self._extract_opportunities(analysis_text),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing route performance: {str(e)}")
            return {"error": str(e)}
    
    def _create_insights_prompt(self, data: Dict) -> str:
        """Create prompt for general market insights"""
        prompt = f"""
        Analyze the following airline booking market data for Australia and provide key insights:

        Total Flights: {data.get('total_flights', 0)}
        Domestic Flights: {data.get('domestic_flights', 0)}
        International Flights: {data.get('international_flights', 0)}
        Average Price: ${data.get('average_price', 0):.2f}
        Price Range: ${data.get('price_range', {}).get('min', 0):.2f} - ${data.get('price_range', {}).get('max', 0):.2f}

        Popular Routes:
        {self._format_popular_routes(data.get('popular_routes', []))}

        Price Trends:
        {json.dumps(data.get('price_trends', {}), indent=2)}

        Seasonal Patterns:
        {json.dumps(data.get('seasonal_patterns', {}), indent=2)}

        Demand Patterns:
        {json.dumps(data.get('demand_patterns', {}), indent=2)}

        Please provide:
        1. Key market trends and insights
        2. Opportunities for hostel businesses
        3. Peak demand periods to watch
        4. Recommendations for monitoring specific routes
        5. Pricing observations and implications

        Keep insights practical and actionable for hostel businesses monitoring travel demand.
        """
        return prompt
    
    def _create_price_trend_prompt(self, route_data: List[Dict]) -> str:
        """Create prompt for price trend analysis"""
        route_info = "\n".join([
            f"Route: {route['origin']} → {route['destination']}, "
            f"Avg Price: ${route.get('average_price', 0):.2f}, "
            f"Flights: {route.get('total_flights', 0)}, "
            f"Demand Score: {route.get('average_demand_score', 0):.1f}"
            for route in route_data[:10]  # Top 10 routes
        ])
        
        prompt = f"""
        Analyze the following route pricing data and identify trends:

        {route_info}

        Please provide:
        1. Price trend analysis across routes
        2. Identify underpriced/overpriced routes
        3. Seasonal pricing patterns
        4. Recommendations for price monitoring
        5. Market opportunities based on pricing

        Focus on actionable insights for business planning.
        """
        return prompt
    
    def _create_forecast_prompt(self, historical_data: Dict) -> str:
        """Create prompt for demand forecasting"""
        prompt = f"""
        Based on the following historical airline booking data, provide demand forecasts:

        Historical Data Summary:
        {json.dumps(historical_data, indent=2)}

        Please provide:
        1. Short-term demand forecast (next 3 months)
        2. Seasonal demand predictions
        3. Key factors influencing demand
        4. Risk factors and uncertainties
        5. Confidence levels for predictions

        Focus on practical forecasts that can guide business decisions.
        """
        return prompt
    
    def _create_route_analysis_prompt(self, route_metrics: List[Dict]) -> str:
        """Create prompt for route performance analysis"""
        route_summary = "\n".join([
            f"Route: {route['origin']} → {route['destination']}, "
            f"Popularity Score: {route.get('route_popularity_score', 0):.1f}, "
            f"Avg Price: ${route.get('average_price', 0):.2f}, "
            f"Total Flights: {route.get('total_flights', 0)}"
            for route in route_metrics[:15]  # Top 15 routes
        ])
        
        prompt = f"""
        Analyze the following route performance data:

        {route_summary}

        Please provide:
        1. Top performing routes and why
        2. Underperforming routes with potential
        3. New route opportunities
        4. Seasonal route performance patterns
        5. Strategic recommendations for route monitoring

        Focus on identifying growth opportunities and market gaps.
        """
        return prompt
    
    def _format_popular_routes(self, popular_routes: List[Dict]) -> str:
        """Format popular routes for prompt"""
        if not popular_routes:
            return "No route data available"
        
        formatted = []
        for route in popular_routes[:5]:  # Top 5 routes
            formatted.append(f"- {route['origin']} → {route['destination']}: {route['flight_count']} flights")
        
        return "\n".join(formatted)
    
    def _parse_insights(self, insight_text: str) -> List[Dict]:
        """Parse insights from AI response"""
        try:
            # Simple parsing - in a real implementation, you might use more sophisticated NLP
            insights = []
            
            # Split by numbered points
            sections = insight_text.split('\n')
            current_insight = None
            
            for section in sections:
                section = section.strip()
                if section and (section[0].isdigit() or section.startswith('-')):
                    if current_insight:
                        insights.append(current_insight)
                    
                    current_insight = {
                        "title": section[:100],  # First 100 chars as title
                        "content": section,
                        "type": "insight"
                    }
                elif current_insight and section:
                    current_insight["content"] += f"\n{section}"
            
            if current_insight:
                insights.append(current_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error parsing insights: {str(e)}")
            return []
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from analysis"""
        try:
            recommendations = []
            lines = analysis_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'recommend' in line.lower() or 'should' in line.lower() or 'suggest' in line.lower():
                    recommendations.append(line)
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error extracting recommendations: {str(e)}")
            return []
    
    def _extract_key_factors(self, forecast_text: str) -> List[str]:
        """Extract key factors from forecast"""
        try:
            factors = []
            lines = forecast_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'factor' in line.lower() or 'influence' in line.lower() or 'impact' in line.lower():
                    factors.append(line)
            
            return factors[:5]  # Top 5 factors
            
        except Exception as e:
            logger.error(f"Error extracting key factors: {str(e)}")
            return []
    
    def _extract_top_routes(self, analysis_text: str) -> List[str]:
        """Extract top routes from analysis"""
        try:
            routes = []
            lines = analysis_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if '→' in line or 'route' in line.lower():
                    routes.append(line)
            
            return routes[:5]  # Top 5 routes
            
        except Exception as e:
            logger.error(f"Error extracting top routes: {str(e)}")
            return []
    
    def _extract_opportunities(self, analysis_text: str) -> List[str]:
        """Extract opportunities from analysis"""
        try:
            opportunities = []
            lines = analysis_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'opportunity' in line.lower() or 'potential' in line.lower() or 'growth' in line.lower():
                    opportunities.append(line)
            
            return opportunities[:5]  # Top 5 opportunities
            
        except Exception as e:
            logger.error(f"Error extracting opportunities: {str(e)}")
            return []
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score based on data quality"""
        try:
            score = 0.5  # Base confidence
            
            # Data completeness
            if data.get('total_flights', 0) > 100:
                score += 0.2
            elif data.get('total_flights', 0) > 50:
                score += 0.1
            
            # Route diversity
            if len(data.get('popular_routes', [])) > 5:
                score += 0.1
            
            # Price data quality
            if data.get('average_price', 0) > 0:
                score += 0.1
            
            # Seasonal data
            if data.get('seasonal_patterns', {}):
                score += 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.5

# Create service instance
openai_service = OpenAIService() 