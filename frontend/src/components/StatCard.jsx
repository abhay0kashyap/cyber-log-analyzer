import React from "react";

const StatCard = ({ title, value }) => {
  return (
    <div className="stat-card">
      <p className="stat-title">{title}</p>
      <h2>{value}</h2>
    </div>
  );
};

export default StatCard;
