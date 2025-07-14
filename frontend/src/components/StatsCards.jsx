import React from 'react';

const StatsCards = ({ data, loading }) => {
  const StatCard = ({ title, value, loading }) => (
    <div className="col-md-3 mb-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <div className="stat-value h3 text-primary mb-1">
            {loading ? (
              <i className="fas fa-spinner fa-spin"></i>
            ) : (
              value?.toLocaleString() || '0'
            )}
          </div>
          <div className="stat-label text-muted small">{title}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="row mb-4">
      <StatCard
        title="Total Flights"
        value={data?.total_flights}
        loading={loading}
      />
      <StatCard
        title="Domestic Routes"
        value={data?.domestic_flights}
        loading={loading}
      />
      <StatCard
        title="International Routes"
        value={data?.international_flights}
        loading={loading}
      />
      <StatCard
        title="Average Price (AUD)"
        value={data?.price_stats?.average ? `$${Math.round(data.price_stats.average)}` : '$0'}
        loading={loading}
      />
    </div>
  );
};

export default StatsCards; 