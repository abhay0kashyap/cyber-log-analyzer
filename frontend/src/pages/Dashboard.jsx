import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";

const Dashboard = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stats")
      .then((res) => res.json())
      .then((data) => setStats(data));
  }, []);

  if (!stats) return <p>Loading...</p>;

  return (
    <div className="dashboard">
      <h1>Cyber Log Analyzer</h1>

      <div className="card-grid">
        <StatCard title="Total Events" value={stats.total_events} />
        <StatCard title="Windows Events" value={stats.windows_events} />
        <StatCard title="Syslog Events" value={stats.syslog_events} />
        <StatCard title="All Devices" value={stats.all_devices} />
      </div>
    </div>
  );
};

export default Dashboard;
