# 📊 Australian Airline Market Demand Analysis Dashboard

A comprehensive web application for analyzing airline booking market demand trends in Australia, featuring real-time flight data analysis, pricing trends, and AI-generated market insights.

## 🚀 Features

### **Backend (FastAPI + SQLite)**
- **Flight Data Collection**: Automated flight data scraping and storage
- **Market Analysis**: Advanced demand metrics and seasonal pattern analysis
- **AI Insights**: OpenAI-powered market trend analysis and recommendations
- **RESTful API**: Comprehensive endpoints for data access and filtering
- **Database Management**: SQLite with SQLAlchemy ORM for efficient data handling

### **Frontend (React + Vite)**
- **Interactive Dashboard**: Real-time data visualization with multiple chart types
- **Responsive Design**: Bootstrap-powered responsive UI that works on all devices
- **Real-time Updates**: Dynamic chart updates based on user-selected filters
- **Modern UI**: Beautiful gradient themes with smooth animations

## 📈 Dashboard Components

### **1. Statistics Cards**
- Total flights tracked
- Domestic vs International breakdown
- Average pricing information
- Recent activity metrics

### **2. Price Trends Chart (Line Chart)**
Shows price variations over time periods:
- **7 Days**: Recent price movements and volatility
- **30 Days**: Medium-term pricing trends
- **90 Days**: Long-term market patterns
- **Features**: Interactive tooltips, responsive scaling

### **3. Route Popularity Chart (Bar Chart)**
Displays top flight routes by volume:
- Flight counts per route
- Average pricing per route
- Demand scores for route popularity
- **Time-filtered**: Shows different routes based on selected period

### **4. Demand Heatmap**
Visual representation of demand patterns:
- **Origin vs Destination**: Matrix showing route demand scores
- **Color-coded**: Intensity represents demand levels
- **Interactive**: Hover for detailed demand metrics

### **5. Seasonal Patterns Chart (Doughnut Chart)**
Analyzes seasonal demand variations:

#### **🌍 What is Seasonal Data?**

**Seasonal patterns** represent how flight demand changes throughout different times of the year in Australia (Southern Hemisphere):

- **Summer (Dec-Feb)**: Peak holiday season, highest demand
  - Beach destinations popular
  - International travel to escape heat
  - Family vacation period

- **Autumn (Mar-May)**: Moderate demand
  - Pleasant weather for travel
  - Business travel picks up post-holidays
  - Shoulder season pricing

- **Winter (Jun-Aug)**: Lower demand period
  - Cooler weather reduces leisure travel
  - Business travel focused on major cities
  - Lowest pricing typically observed

- **Spring (Sep-Nov)**: Growing demand
  - Weather improving, travel increasing
  - Spring break and holiday planning
  - Melbourne Cup and other events

#### **🏖️ Holiday vs Regular Periods**
- **Holiday Periods**: School holidays, public holidays, weekends
- **Regular Periods**: Business days, normal travel patterns
- **Insight**: Shows how special events affect flight demand and pricing

### **6. AI-Generated Insights**
- Market trend analysis
- Pricing recommendations
- Demand predictions
- Route optimization suggestions

## 🔄 Frontend Architecture Evolution

 **React + Vite** architecture for better reliability:

**Key Improvements:**
- **Component Lifecycle**: Proper chart creation/destruction through useEffect
- **State Management**: useState and useEffect for reactive updates
- **Filter Integration**: Charts automatically re-render when filters change
- **Memory Management**: Automatic cleanup when components unmount
- **Code Organization**: Clean separation of concerns with reusable components

## 🛠️ Technical Stack

### **Backend**
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Pydantic**: Data validation and settings management
- **OpenAI API**: AI-powered insights generation
- **Amadeus API**: Flight data source

### **Frontend**
- **React 18**: Modern JavaScript library
- **Vite**: Fast build tool and dev server
- **Chart.js + react-chartjs-2**: Interactive charts
- **Plotly.js**: Advanced heatmap visualizations
- **Bootstrap 5**: Responsive CSS framework
- **Axios**: HTTP client for API calls

## 🎯 Filter System

### **Time Period Filter**
The main filtering mechanism allows users to analyze data across different timeframes:

- **7 Days**: Shows recent trends and short-term patterns
  - Example: Recent 8 dates with 423 total flights
  - Price range: $253-$498 per day
  
- **30 Days**: Medium-term analysis for monthly patterns
  - Example: 16 dates with 567 total flights
  - Comprehensive price trends over time
  
- **90 Days**: Long-term trend analysis
  - Historical patterns and seasonal effects
  - Complete market cycle analysis

**How It Works:**
- Backend filters flights by `departure_date` within the specified period
- All charts update simultaneously with new data
- Route popularity rankings change based on time period
- Price trends show actual historical progression

## 🏗️ Component Architecture

### **Dashboard.jsx** (Main Container)
```javascript
- State management for filters and data
- API integration and error handling
- Alert system for user notifications
- Centralized loading states
```

### **Chart Components**
```javascript
PriceTrendChart.jsx     // Line chart for price trends
RoutePopularityChart.jsx // Bar chart for route popularity  
DemandHeatmap.jsx       // Plotly heatmap for demand analysis
SeasonalChart.jsx       // Doughnut chart for seasonal patterns
```

### **Supporting Components**
```javascript
FilterPanel.jsx    // Time period selection
StatsCards.jsx     // Summary statistics display
Navbar.jsx         // Header with refresh controls
AlertManager.jsx   // Notification system
LoadingModal.jsx   // Loading state management
```

## 🎨 UI/UX Features

### **Responsive Design**
- **Mobile-first**: Works seamlessly on phones, tablets, and desktops
- **Bootstrap Grid**: Flexible layout that adapts to screen size
- **Touch-friendly**: Large tap targets and intuitive interactions

### **Visual Design**
- **Gradient Themes**: Modern purple-blue gradient backgrounds
- **Card Layout**: Clean, organized information display
- **Interactive Elements**: Hover effects and smooth transitions
- **Loading States**: Clear feedback during data loading

### **User Experience**
- **Real-time Updates**: Charts update immediately when filters change
- **Progress Feedback**: Loading spinners and success notifications
- **Error Handling**: Graceful error messages and fallbacks
- **Accessibility**: Screen reader friendly and keyboard navigation

## 📊 Data Analysis Insights

### **Market Trends**
- **Domestic Routes**: SYD↔MEL, SYD↔BNE, MEL↔BNE most popular
- **International Routes**: Australia to SIN, LAX, LHR destinations
- **Pricing Patterns**: Peak hours (early morning/evening) cost 20% more
- **Seasonal Effects**: Winter (current) shows lower demand scores

### **Business Intelligence**
- **Route Performance**: Track which routes are gaining/losing popularity
- **Price Optimization**: Identify optimal pricing windows
- **Demand Forecasting**: Seasonal and holiday period planning
- **Capacity Planning**: Understand peak travel periods

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- npm or yarn

### **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python run.py
# Server runs on http://localhost:8002
```

### **Frontend Setup**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:5173
```

### **Access the Application**
- **Dashboard**: http://localhost:5173
- **API Documentation**: http://localhost:8002/docs
- **API Base URL**: http://localhost:8002/api

## 📱 Usage

1. **Access Dashboard**: Open http://localhost:5173 in your browser
2. **Select Time Period**: Choose 7, 30, or 90 days from the filter dropdown
3. **View Charts**: All charts update automatically with filtered data
4. **Analyze Trends**: 
   - Price trends show market movements over time
   - Route popularity reveals top destinations
   - Seasonal patterns show demand cycles
   - Demand heatmap identifies high-traffic routes
5. **Generate Insights**: Click "Generate New Insights" for AI analysis

## 🔍 API Endpoints

### **Chart Data**
- `GET /api/charts/price-trends?days={period}` - Price trend data
- `GET /api/charts/route-popularity?days={period}&limit=5` - Route popularity
- `GET /api/charts/demand-heatmap?days={period}` - Demand heatmap data
- `GET /api/charts/seasonal-patterns?days={period}` - Seasonal analysis

### **Dashboard Data**
- `GET /api/dashboard/summary` - Summary statistics
- `GET /api/insights?limit=5` - AI-generated insights

### **Data Management**
- `POST /api/fetch-flights` - Trigger new data collection
- `POST /api/insights/generate` - Generate new AI insights

## 🧪 Data Examples

### **Price Trends Response**
```json
{
  "dates": ["2025-07-07", "2025-07-08", "2025-07-09"],
  "prices": [355.53, 442.78, 404.55],
  "flight_counts": [17, 15, 16]
}
```

### **Seasonal Patterns**
```json
{
  "chart_data": [
    {
      "season": "Winter",
      "flight_count": 267,
      "avg_demand": 78.34
    }
  ]
}
```

## 📈 Performance

### **Optimization Features**
- **Efficient Queries**: Indexed database queries with date filtering
- **Lazy Loading**: Charts load data only when needed
- **Caching**: React component memoization for performance
- **Responsive Charts**: Automatic resizing and optimization

### **Scalability**
- **Database**: SQLite easily upgradeable to PostgreSQL
- **API**: FastAPI supports high concurrency
- **Frontend**: React optimized for large datasets
- **Caching**: Ready for Redis integration

## 🔮 Future Enhancements

### **Planned Features**
- **Real-time Data**: WebSocket integration for live updates
- **Advanced Filters**: Airline, aircraft type, booking class filters
- **Predictive Analytics**: Machine learning demand forecasting
- **Export Features**: PDF reports and CSV data export
- **User Accounts**: Personalized dashboards and saved filters

### **Technical Improvements**
- **Database Migration**: Move to PostgreSQL for production
- **Caching Layer**: Redis for improved performance
- **API Rate Limiting**: Enhanced rate limiting and quotas
- **Testing**: Comprehensive unit and integration tests
- **Docker**: Containerization for easy deployment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, email support@example.com or create an issue in the GitHub repository.

---

**Built with ❤️ for Australian aviation market analysis** 