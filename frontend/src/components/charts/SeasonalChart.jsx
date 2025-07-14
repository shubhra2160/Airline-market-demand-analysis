import React, { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const SeasonalChart = ({ filters }) => {
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
      
      const url = `/api/charts/seasonal-patterns?${params}`;
      console.log('Loading seasonal chart with URL:', url);
      console.log('Applied filters:', filters);
      
      const response = await axios.get(url);
      const chartData = response.data;
      
      if (!chartData.chart_data || chartData.chart_data.length === 0) {
        setData(null);
        return;
      }
      
      setData({
        labels: chartData.chart_data.map(item => item.season),
        datasets: [{
          data: chartData.chart_data.map(item => item.flight_count),
          backgroundColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#f5576c'
          ],
          borderColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#f5576c'
          ],
          borderWidth: 1
        }]
      });
    } catch (err) {
      console.error('Error loading seasonal chart:', err);
      setError('Failed to load seasonal data');
    } finally {
      setLoading(false);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
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

  if (!data) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <p className="text-muted">No seasonal data available</p>
      </div>
    );
  }

  return <Doughnut data={data} options={options} />;
};

export default SeasonalChart; 