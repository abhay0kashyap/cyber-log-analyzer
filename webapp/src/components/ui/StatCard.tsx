import React from "react";
import "./StatCard.css";

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  accentColor: "blue" | "red" | "green" | "purple" | "orange";
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  accentColor,
}) => {
  return (
    <div className={`stat-card ${accentColor}`}>
      <div className="stat-card-header">
        <span className="stat-icon">{icon}</span>
        <span className="stat-title">{title}</span>
      </div>
      <div className="stat-value">{value}</div>
    </div>
  );
};

export default StatCard;
