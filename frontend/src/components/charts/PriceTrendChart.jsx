import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PriceTrendChart = ({ filters }) => {
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
      params.append('days', filters.timePeriod || '7');
      
      const url = `/api/charts/price-trends?${params}`;
      console.log('Loading price trend chart with URL:', url);
      console.log('Applied filters:', filters);
      
      const response = await axios.get(url);
      const chartData = response.data;
      
      console.log('Price trends data received:', chartData.chart_data?.dates?.length || 0, 'dates');
      
      if (chartData.chart_data?.dates?.length === 1) {
        console.log('Note: All flight data is from the same day:', chartData.chart_data.dates[0]);
      }
      
      setData({
        labels: chartData.chart_data.dates || [],
        datasets: [{
          label: 'Average Price (AUD)',
          data: chartData.chart_data.prices || [],
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        }]
      });
    } catch (err) {
      console.error('Error loading price trend chart:', err);
      setError('Failed to load price trend data');
    } finally {
      setLoading(false);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: function(value) {
            return '$' + value.toFixed(0);
          }
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context) {
            return 'Price: $' + context.parsed.y.toFixed(2);
          }
        }
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
        <p className="text-muted">No price trend data available for selected filters</p>
      </div>
    );
  }

  return <Line data={data} options={options} />;
};

export default PriceTrendChart; 