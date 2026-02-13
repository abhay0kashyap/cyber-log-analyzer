import { useEffect, useState } from "react";
import LiveChart from "../components/LiveChart";
import StatCard from "../components/StatCard";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);

  // Fetch stats once on load
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/stats")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);

        // Add first chart point
        setChartData([
          {
            time: new Date().toLocaleTimeString(),
            events: data.total_events,
          },
        ]);
      });
  }, []);

  // Update chart every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:8000/api/stats")
        .then((res) => res.json())
        .then((data) => {
          const newPoint = {
            time: new Date().toLocaleTimeString(),
            events: data.total_events,
          };

          setChartData((prev) => [...prev.slice(-10), newPoint]);
        });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!stats) return <p>Loading...</p>;

  return (
    <div style={{ padding: "40px" }}>
      <h1 style={{ marginBottom: "30px" }}>
        Cyber Log Analyzer
      </h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "20px",
        }}
      >
        <StatCard title="Total Events" value={stats.total_events} />
        <StatCard title="Windows Events" value={stats.windows_events} />
        <StatCard title="Syslog Events" value={stats.syslog_events} />
        <StatCard title="All Devices" value={stats.all_devices} />
      </div>

      {/* Chart Below Stats */}
      <LiveChart data={chartData} />
    </div>
  );
};

export default Dashboard;
