import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import StatsCards from './StatsCards';
import FilterPanel from './FilterPanel';
import ChartsSection from './ChartsSection';
import InsightsSection from './InsightsSection';
import LoadingModal from './LoadingModal';
import AlertManager from './AlertManager';

const Dashboard = () => {
  const [data, setData] = useState({
    summary: null,
    insights: []
  });
  
  const [filters, setFilters] = useState({
    timePeriod: '7'
  });
  
  const [loading, setLoading] = useState(false);
  const [showLoadingModal, setShowLoadingModal] = useState(false);
  const [alerts, setAlerts] = useState([]);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Debug filter changes
  useEffect(() => {
    console.log('Dashboard filters updated:', filters);
  }, [filters]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [summaryRes, insightsRes] = await Promise.all([
        axios.get('/api/dashboard/summary'),
        axios.get('/api/insights?limit=5')
      ]);
      
      setData(prev => ({
        ...prev,
        summary: summaryRes.data,
        insights: insightsRes.data.insights
      }));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      showAlert('Error loading dashboard data', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    console.log('Filter change triggered:', newFilters);
    console.log('Previous filters:', filters);
    
    setFilters(newFilters);
    
    // Show filter change notification
    if (newFilters.timePeriod) {
      showAlert(`Time period changed to ${newFilters.timePeriod} days`, 'success');
    }
  };

  const fetchNewData = async () => {
    setShowLoadingModal(true);
    try {
      const response = await axios.post('/api/fetch-flights');
      if (response.status === 200) {
        showAlert('Data fetch started! This will take 5-10 minutes. Please refresh the page later to see new data.', 'info');
        
        // Keep modal open for 3 seconds
        setTimeout(() => {
          setShowLoadingModal(false);
          showAlert('Data fetching in progress in background. Refresh the page in 5-10 minutes to see new data.', 'warning');
        }, 3000);
      }
    } catch (error) {
      console.error('Error fetching new data:', error);
      showAlert('Error fetching new data', 'danger');
      setShowLoadingModal(false);
    }
  };

  const generateInsights = async () => {
    setShowLoadingModal(true);
    try {
      const response = await axios.post('/api/insights/generate');
      if (response.status === 200) {
        await loadDashboardData(); // Reload insights
        showAlert('New insights generated successfully!', 'success');
      } else {
        showAlert('Error generating insights', 'danger');
      }
    } catch (error) {
      console.error('Error generating insights:', error);
      showAlert('Error generating insights', 'danger');
    } finally {
      setShowLoadingModal(false);
    }
  };

  const refreshData = async () => {
    await loadDashboardData();
    showAlert('Dashboard refreshed!', 'success');
  };

  const showAlert = (message, type) => {
    const id = Date.now();
    setAlerts(prev => [...prev, { id, message, type }]);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setAlerts(prev => prev.filter(alert => alert.id !== id));
    }, 5000);
  };

  const dismissAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  return (
    <div className="dashboard">
      <Navbar onRefresh={refreshData} onFetchData={fetchNewData} />
      
      <AlertManager alerts={alerts} onDismiss={dismissAlert} />
      
      <div className="dashboard-header">
        <div className="container">
          <div className="row">
            <div className="col-md-8">
              <h1>📊 Market Demand Dashboard</h1>
              <p className="lead">Real-time analysis of airline booking trends in Australia</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-fluid">
        <StatsCards data={data.summary} loading={loading} />
        
        <FilterPanel 
          filters={filters} 
          onChange={handleFilterChange} 
        />
        
        <ChartsSection filters={filters} />
        
        <InsightsSection 
          insights={data.insights} 
          onGenerateInsights={generateInsights} 
        />
      </div>
      
      <LoadingModal show={showLoadingModal} />
    </div>
  );
};

export default Dashboard; 