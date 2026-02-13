import React from "react";

const Alerts = () => {
  return (
    <div className="page">
      <h1>Security Alerts</h1>

      <div className="alert-card high">
        <h3>Brute Force Attack Detected</h3>
        <p>IP: 192.168.1.45</p>
        <span className="severity">High</span>
      </div>

      <div className="alert-card medium">
        <h3>Multiple Failed Login Attempts</h3>
        <p>IP: 10.0.0.12</p>
        <span className="severity">Medium</span>
      </div>
    </div>
  );
};

export default Alerts;
