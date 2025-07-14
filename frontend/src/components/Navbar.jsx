import React from 'react';

const Navbar = ({ onRefresh, onFetchData }) => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div className="container">
        <a className="navbar-brand fw-bold text-primary" href="#">
          ✈️ Airline Market Analyzer
        </a>
        <div className="navbar-nav ms-auto">
          <button 
            className="btn btn-outline-primary btn-sm me-2" 
            onClick={onRefresh}
          >
            <i className="fas fa-sync-alt"></i> Refresh Data
          </button>
          <button 
            className="btn btn-primary btn-sm" 
            onClick={onFetchData}
          >
            <i className="fas fa-download"></i> Fetch Latest Data
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 