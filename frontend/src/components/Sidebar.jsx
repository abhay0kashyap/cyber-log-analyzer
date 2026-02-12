import React from "react";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2 className="logo">SIEM</h2>

      <nav>
        <a className="nav-item active">Dashboard</a>
        <a className="nav-item">Reports</a>
        <a className="nav-item">Compliance</a>
        <a className="nav-item">Search</a>
        <a className="nav-item">Correlation</a>
        <a className="nav-item">Alerts</a>
        <a className="nav-item">Settings</a>
      </nav>
    </div>
  );
};

export default Sidebar;
