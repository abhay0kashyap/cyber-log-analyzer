import React from "react";
import StatCard from "../components/StatCard";

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1 className="page-title">Cyber Log Analyzer</h1>

      <div className="cards-grid">
        <StatCard title="Total Events" value="7,333K" />
        <StatCard title="Windows Events" value="6,407K" />
        <StatCard title="Syslog Events" value="269K" />
        <StatCard title="All Devices" value="44" />
      </div>
    </div>
  );
};

export default Dashboard;
