import { useCallback, useEffect, useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import EventChart from '../components/EventChart';
import GeoThreatMap from '../components/GeoThreatMap';
import StatCard from '../components/StatCard';
import TopAttackingIps from '../components/TopAttackingIps';
import { api } from '../services/api';
import { SEVERITY_COLORS } from '../utils/severity';

const emptyMetrics = {
  total_events: 0,
  windows_events: 0,
  syslog_events: 0,
  devices: 0,
  severity_distribution: { low: 0, medium: 0, high: 0, critical: 0 },
  attack_timeline: [],
  top_ips: [],
  recent_activity: false,
  recent_alerts: [],
};

function Dashboard({ onSyncTick }) {
  const [range, setRange] = useState('24h');
  const [metrics, setMetrics] = useState(emptyMetrics);
  const [geoFeed, setGeoFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const loadDashboard = useCallback(async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const [metricsPayload, geoPayload] = await Promise.all([
        api.getMetrics(range),
        api.getGeoFeed(range),
      ]);
      setMetrics(metricsPayload);
      setGeoFeed(geoPayload.records || []);
      setError('');
      onSyncTick?.();
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      if (isFirst) setLoading(false);
    }
  }, [onSyncTick, range]);

  useEffect(() => {
    loadDashboard(true);
  }, [loadDashboard]);

  useEffect(() => {
    const socket = api.connectUpdates(() => {
      loadDashboard(false);
    });

    return () => {
      socket?.close();
    };
  }, [loadDashboard]);

  const severityForView = useMemo(
    () => ({
      Critical: Number(metrics.severity_distribution?.critical || 0),
      High: Number(metrics.severity_distribution?.high || 0),
      Medium: Number(metrics.severity_distribution?.medium || 0),
      Low: Number(metrics.severity_distribution?.low || 0),
    }),
    [metrics.severity_distribution]
  );

  const severityData = useMemo(
    () => Object.entries(severityForView).map(([name, value]) => ({ name, value })),
    [severityForView]
  );

  const attackTypeData = useMemo(() => {
    const counts = (metrics.recent_alerts || []).reduce((acc, alert) => {
      const type = alert.type || 'unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [metrics.recent_alerts]);

  const timelineData = useMemo(
    () => (metrics.attack_timeline || []).map((point) => ({ time: point.timestamp, alerts: point.count })),
    [metrics.attack_timeline]
  );

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError('');
      const result = await api.uploadLog(file);

      if (result.metrics) {
        setMetrics(result.metrics);
      }

      await loadDashboard(false);
      setMessage(`Ingested ${result.ingested_events} events and generated ${result.generated_alerts} alerts.`);
      setTimeout(() => setMessage(''), 3500);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-soc-muted">SOC Situation Room</h2>
        <div className="flex flex-wrap gap-2">
          <select className="soc-input" value={range} onChange={(e) => setRange(e.target.value)}>
            <option value="1h">Last 1 hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="week">Last 7 days</option>
          </select>
          <label className="soc-button cursor-pointer border-blue-400/50 text-blue-300">
            {uploading ? 'Uploading...' : 'Upload Logs'}
            <input className="hidden" type="file" accept=".log,.txt,.csv,.json" onChange={handleUpload} />
          </label>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {loading ? (
          <>
            <div className="soc-card h-28 animate-pulse" />
            <div className="soc-card h-28 animate-pulse" />
            <div className="soc-card h-28 animate-pulse" />
            <div className="soc-card h-28 animate-pulse" />
          </>
        ) : (
          <>
            <StatCard title="Total Events" value={metrics.total_events} accent="#3b82f6" subtitle="Collected logs" />
            <StatCard title="Windows Events" value={metrics.windows_events} accent="#2ecc71" subtitle="Endpoint telemetry" />
            <StatCard title="Syslog Events" value={metrics.syslog_events} accent="#ffd60a" subtitle="Network / Linux logs" />
            <StatCard title="Devices" value={metrics.devices} accent="#ff8c00" subtitle="Active assets" />
          </>
        )}
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <EventChart data={timelineData} title="Attack Timeline" />
        </div>

        <section className="soc-card h-80 p-4">
          <h3 className="text-sm font-semibold text-soc-text">Attack Type Distribution</h3>
          <div className="mt-2 h-[88%]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={attackTypeData} dataKey="value" nameKey="name" outerRadius={96}>
                  {attackTypeData.map((entry, idx) => {
                    const palette = ['#3b82f6', '#ff3b3b', '#ff8c00', '#ffd60a', '#2ecc71', '#8b5cf6'];
                    return <Cell key={`${entry.name}-${idx}`} fill={palette[idx % palette.length]} />;
                  })}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <section className="soc-card p-4">
          <h3 className="text-sm font-semibold text-soc-text">Severity Distribution</h3>
          <div className="mt-3 space-y-2">
            {severityData.map((item) => (
              <div key={item.name} className="rounded-lg border border-soc-border bg-soc-panelSoft/50 px-3 py-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-soc-muted">{item.name}</span>
                  <span className="font-semibold" style={{ color: SEVERITY_COLORS[item.name] }}>
                    {item.value}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-2">
          <p className={`text-sm ${metrics.recent_activity ? 'text-[#ffb35a]' : 'text-soc-muted'}`}>
            {metrics.recent_activity ? 'Active attacks detected' : 'No attack activity in last 10 minutes'}
          </p>
          <TopAttackingIps ips={metrics.top_ips || []} />
        </section>

        <GeoThreatMap geoSources={geoFeed} />
      </section>

      <section className="soc-card p-4">
        <h3 className="text-sm font-semibold text-soc-text">Recent Alerts</h3>
        <div className="mt-3 grid gap-2 lg:grid-cols-2">
          {(metrics.recent_alerts || []).length === 0 ? (
            <p className="text-sm text-soc-muted">No alerts in selected time window.</p>
          ) : (
            metrics.recent_alerts.slice(0, 8).map((alert) => (
              <div key={alert.id} className="rounded-xl border border-soc-border bg-soc-panelSoft/55 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-soc-text">{alert.type}</p>
                  <span className="text-xs" style={{ color: SEVERITY_COLORS[alert.severity] }}>
                    {alert.severity}
                  </span>
                </div>
                <p className="mt-1 text-xs text-soc-muted">{alert.ip} • {new Date(alert.timestamp).toLocaleString()}</p>
                <p className="mt-1 text-xs text-soc-muted">{alert.message}</p>
              </div>
            ))
          )}
        </div>
      </section>

      {message ? <p className="text-sm text-blue-300">{message}</p> : null}
      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
    </div>
  );
}

export default Dashboard;
