import React from 'react';

const AlertManager = ({ alerts, onDismiss }) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="alert-container position-fixed top-0 start-50 translate-middle-x" style={{ zIndex: 1050, marginTop: '80px' }}>
      {alerts.map(alert => (
        <div 
          key={alert.id}
          className={`alert alert-${alert.type} alert-dismissible fade show mb-2`}
          role="alert"
        >
          {alert.message}
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => onDismiss(alert.id)}
            aria-label="Close"
          ></button>
        </div>
      ))}
    </div>
  );
};

export default AlertManager; 