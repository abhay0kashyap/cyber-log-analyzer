import React, { useEffect, useState } from "react";
import MainLayout from "../layout/MainLayout";
import api from "../services/api";

interface Stats {
  total_events: number;
  total_attacks: number;
  unique_ips: number;
  active_alerts: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const statsData = await api.getStats();
        const alertsData = await api.getAlerts({ active_only: true });
        setStats(statsData);
        setAlerts(alertsData);
      } catch (err) {
        console.error(err);
      }
    };

    loadData();
  }, []);

  return (
    <MainLayout>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <h1 style={{ marginBottom: "30px" }}>Security Overview</h1>

        {/* ===== STATS GRID ===== */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "20px",
            marginBottom: "40px",
          }}
        >
          <StatCard title="Total Events" value={stats?.total_events} />
          <StatCard title="Attacks Detected" value={stats?.total_attacks} />
          <StatCard title="Unique IPs" value={stats?.unique_ips} />
          <StatCard title="Active Alerts" value={stats?.active_alerts} />
        </div>

        {/* ===== ALERTS SECTION ===== */}
        <div>
          <h2 style={{ marginBottom: "20px" }}>Active Alerts</h2>

          <div
            style={{
              background: "#111827",
              borderRadius: "10px",
              padding: "20px",
            }}
          >
            {alerts.length === 0 && (
              <p style={{ color: "#9ca3af" }}>No active alerts</p>
            )}

            {alerts.map((alert) => (
              <div
                key={alert.id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "15px 0",
                  borderBottom: "1px solid #1f2937",
                }}
              >
                <div>
                  <strong>{alert.alert_type}</strong>
                  <p style={{ color: "#9ca3af", margin: 0 }}>
                    {alert.description}
                  </p>
                </div>

                <div
                  style={{
                    padding: "6px 12px",
                    borderRadius: "6px",
                    fontSize: "12px",
                    background:
                      alert.severity === "high"
                        ? "#7f1d1d"
                        : alert.severity === "medium"
                        ? "#78350f"
                        : "#1e3a8a",
                  }}
                >
                  {alert.severity.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;

/* ===== STAT CARD COMPONENT ===== */

const StatCard = ({
  title,
  value,
}: {
  title: string;
  value?: number;
}) => {
  return (
    <div
      style={{
        background: "#111827",
        padding: "25px",
        borderRadius: "12px",
        boxShadow: "0 0 15px rgba(0,0,0,0.3)",
      }}
    >
      <p style={{ color: "#9ca3af", marginBottom: "10px" }}>{title}</p>
      <h2 style={{ margin: 0 }}>{value ?? 0}</h2>
    </div>
  );
};
