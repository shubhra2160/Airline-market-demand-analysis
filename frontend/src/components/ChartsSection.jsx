import React from 'react';
import PriceTrendChart from './charts/PriceTrendChart';
import RoutePopularityChart from './charts/RoutePopularityChart';
import DemandHeatmap from './charts/DemandHeatmap';
import SeasonalChart from './charts/SeasonalChart';

const ChartsSection = ({ filters }) => {
  // Create a key based on filter values to force re-render when filters change
  const filterKey = JSON.stringify(filters);
  
  return (
    <>
      {/* Charts Row 1 */}
      <div className="row mb-3">
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title">📈 Price Trends Over Time</h5>
              <div style={{ height: '300px' }}>
                <PriceTrendChart key={`price-${filterKey}`} filters={filters} />
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title">🔥 Route Popularity</h5>
              <div style={{ height: '300px' }}>
                <RoutePopularityChart key={`route-${filterKey}`} filters={filters} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="row mb-3">
        <div className="col-lg-6">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title">🗺️ Demand Heatmap</h5>
              <div style={{ height: '300px' }}>
                <DemandHeatmap key={`heatmap-${filterKey}`} filters={filters} />
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title">🌍 Seasonal Patterns</h5>
              <div style={{ height: '300px' }}>
                <SeasonalChart key={`seasonal-${filterKey}`} filters={filters} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ChartsSection; 