import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const RoutePopularityChart = ({ filters }) => {
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
      params.append('limit', '5');
      
      // Add time period filter
      if (filters.timePeriod) {
        params.append('days', filters.timePeriod);
      }
      
      const url = `/api/charts/route-popularity?${params}`;
      console.log('Loading route popularity chart with URL:', url);
      console.log('Applied filters:', filters);
      
      const response = await axios.get(url);
      const chartData = response.data;
      
      console.log('Route popularity data received:', chartData.chart_data?.length || 0, 'routes');
      
      setData({
        labels: chartData.chart_data?.map(item => item.route) || [],
        datasets: [{
          label: 'Flight Count',
          data: chartData.chart_data?.map(item => item.flight_count) || [],
          backgroundColor: 'rgba(102, 126, 234, 0.8)',
          borderColor: '#667eea',
          borderWidth: 1
        }]
      });
    } catch (err) {
      console.error('Error loading route popularity chart:', err);
      setError('Failed to load route popularity data');
    } finally {
      setLoading(false);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        display: false
      }
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

  if (!data || !data.labels || data.labels.length === 0) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <p className="text-muted">No route data available for selected filters</p>
      </div>
    );
  }

  return <Bar data={data} options={options} />;
};

export default RoutePopularityChart; 