import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

const DemandHeatmap = ({ filters }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadChartData();
  }, [filters]);

  const loadChartData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Build query parameters
      const params = new URLSearchParams();
      
      // Add time period filter
      if (filters.timePeriod) {
        params.append('days', filters.timePeriod);
      }
      
      const url = `/api/charts/demand-heatmap?${params}`;
      console.log('Loading demand heatmap with URL:', url);
      console.log('Applied filters:', filters);
      
      const response = await axios.get(url);
      const chartData = response.data;
      
      if (!chartData.heatmap_data || chartData.heatmap_data.length === 0) {
        setData(null);
        return;
      }
      
      // Create matrix
      const z = [];
      const x = chartData.origins;
      const y = chartData.destinations;
      
      for (let i = 0; i < y.length; i++) {
        z[i] = [];
        for (let j = 0; j < x.length; j++) {
          const point = chartData.heatmap_data.find(item => 
            item.origin === x[j] && item.destination === y[i]
          );
          z[i][j] = point ? point.demand_score : 0;
        }
      }
      
      setData({
        data: [{
          x: x,
          y: y,
          z: z,
          type: 'heatmap',
          colorscale: [
            [0, '#f8f9fa'],
            [0.5, '#667eea'],
            [1, '#764ba2']
          ],
          showscale: true
        }],
        layout: {
          title: '',
          xaxis: { title: 'Origin' },
          yaxis: { title: 'Destination' },
          margin: { l: 60, r: 60, t: 20, b: 60 }
        }
      });
    } catch (err) {
      console.error('Error loading demand heatmap:', err);
      setError('Failed to load demand heatmap data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <p className="text-danger">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <p className="text-muted">No demand data available</p>
      </div>
    );
  }

  return (
    <Plot
      data={data.data}
      layout={{
        ...data.layout,
        autosize: true,
        height: 280,
        responsive: true
      }}
      style={{ width: '100%', height: '100%' }}
      config={{ responsive: true }}
    />
  );
};

export default DemandHeatmap; 