import React from 'react';

const FilterPanel = ({ filters, onChange }) => {
  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    onChange(newFilters);
  };

  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="card border-0 shadow-sm">
          <div className="card-body">
            <h5 className="card-title mb-3">🔍 Filters & Controls</h5>
            <div className="row">
              <div className="col-md-4">
                <label className="form-label">Time Period</label>
                <select 
                  className="form-select"
                  value={filters.timePeriod}
                  onChange={(e) => handleFilterChange('timePeriod', e.target.value)}
                >
                  <option value="7">Last 7 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                </select>
              </div>
              <div className="col-md-8">
                <div className="d-flex align-items-end h-100">
                  <div className="text-muted">
                    <small>📊 Showing flight data and trends for the selected time period</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel; 