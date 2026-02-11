import React from "react";

type StatCardProps = {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  accentColor: "critical" | "warning" | "info" | "success" | "accent";
};

const accentClasses = {
  critical: "stat-card-critical",
  warning: "stat-card-warning",
  info: "stat-card-info",
  success: "stat-card-success",
  accent: "stat-card-accent",
};

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  accentColor,
}) => {
  const accentClass = accentClasses[accentColor];

  return (
    <div
      className={`
        bg-panels-cards border border-borders rounded-2xl p-5
        flex items-center space-x-4
        transition-all duration-300
        hover:shadow-lg hover:shadow-accent-intelligence/10 hover:border-accent-intelligence/50
        border-l-4 ${accentClass}
      `}
      style={{
        backgroundColor: 'var(--panels-cards)',
      }}
    >
      <div className="flex-shrink-0 text-text-muted">{icon}</div>
      <div>
        <p className="text-sm text-text-muted font-medium uppercase tracking-wider">
          {title}
        </p>
        <p className="text-4xl font-extrabold text-text-primary">
          {value}
        </p>
      </div>
    </div>
  );
};

export default StatCard;
