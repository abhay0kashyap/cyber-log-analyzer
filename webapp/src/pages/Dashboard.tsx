import React, { useEffect, useState } from "react";
import api, { Stats, Alert as AlertType } from "../services/api";
import StatCard from "../components/ui/StatCard";
import "./Dashboard.css";

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, alertsData] = await Promise.all([
          api.getStats(),
          api.getAlerts({ active_only: true }),
        ]);

        setStats(statsData);
        setAlerts(alertsData);
        setError(null);
      } catch (err) {
        setError("Failed to fetch data from backend. Is it running?");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p className="status-text">Loading dashboard…</p>;
  if (error) return <p className="error-text">{error}</p>;
  if (!stats) return null;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Cyber Log Analyzer</h1>
        <p>SIEM-style Security Monitoring Dashboard</p>
        <span className="backend-status online">● Backend Connected</span>
      </header>

      {/* Stats Grid */}
      <section className="stats-grid">
        <StatCard
          title="Total Events"
          value={stats.total_events}
          icon="📊"
          accentColor="blue"
        />
        <StatCard
          title="Attacks Detected"
          value={stats.total_attacks}
          icon="⚠️"
          accentColor="red"
        />
        <StatCard
          title="Unique IPs"
          value={stats.unique_ips}
          icon="🌐"
          accentColor="purple"
        />
        <StatCard
          title="Active Alerts"
          value={stats.active_alerts}
          icon="🚨"
          accentColor="orange"
        />
      </section>

      {/* Alerts Section */}
      <section className="alerts-section">
        <h2>🚨 Active Alerts</h2>

        {alerts.length === 0 && (
          <p className="muted">No active alerts 🎉</p>
        )}

        {alerts.map((alert) => (
          <div key={alert.id} className={`alert-card ${alert.severity}`}>
            <div>
              <strong>{alert.alert_type}</strong>
              <p className="muted">{alert.description}</p>
              <span className="ip">IP: {alert.source_ip}</span>
            </div>
            <span className={`severity-badge ${alert.severity}`}>
              {alert.severity.toUpperCase()}
            </span>
          </div>
        ))}
      </section>
    </div>
  );
};

export default Dashboard;
