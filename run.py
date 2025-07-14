#!/usr/bin/env python3
"""
Airline Booking Market Demand Analyzer - Run Script
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🛫 Starting Airline Booking Market Demand Analyzer...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print("📊 Access the dashboard at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("-" * 50)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 