import React from 'react';

const InsightsSection = ({ insights, onGenerateInsights }) => {
  const getBadgeClass = (priority) => {
    switch(priority) {
      case 'high': return 'bg-danger';
      case 'medium': return 'bg-warning';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="card border-0 shadow-sm">
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="card-title mb-0">🤖 AI-Generated Insights</h5>
              <button 
                className="btn btn-primary btn-sm" 
                onClick={onGenerateInsights}
              >
                <i className="fas fa-brain"></i> Generate New Insights
              </button>
            </div>
            
            <div className="insights-container">
              {!insights || insights.length === 0 ? (
                <p className="text-muted">
                  No insights available. Click "Generate New Insights" to create some.
                </p>
              ) : (
                insights.map((insight, index) => (
                  <div key={index} className="insight-card card border-start border-success border-3 mb-3">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <h6 className="card-title">{insight.title}</h6>
                          <p className="card-text">{insight.content}</p>
                          <small className="text-muted">
                            {insight.category} • Confidence: {Math.round(insight.confidence_score * 100)}%
                          </small>
                        </div>
                        <span className={`badge ${getBadgeClass(insight.priority)} ms-2`}>
                          {insight.priority}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsightsSection; 