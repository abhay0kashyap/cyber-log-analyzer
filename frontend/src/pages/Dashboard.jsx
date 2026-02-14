import { useCallback, useEffect, useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import EventChart from '../components/EventChart';
import GeoThreatMap from '../components/GeoThreatMap';
import StatCard from '../components/StatCard';
import TopAttackingIps from '../components/TopAttackingIps';
import { api } from '../services/api';
import { SEVERITY_COLORS } from '../utils/severity';

function mapSeverityToDashboard(severity = {}) {
  return {
    Critical: Number(severity.critical || 0),
    High: Number(severity.high || 0),
    Medium: Number(severity.medium || 0),
    Low: Number(severity.low || 0),
  };
}

function mapTopIps(topIps = []) {
  return topIps.map((row) => {
    const count = Number(row.count || 0);
    return {
      ip: row.ip,
      count,
      attack_score: count,
      critical_count: 0,
      high_count: 0,
      high_risk: false,
    };
  });
}

function mapAlerts(alerts = []) {
  return alerts.map((alert, index) => ({
    id: alert.id || `${alert.ip || 'unknown'}-${alert.timestamp || index}-${index}`,
    timestamp: alert.timestamp || new Date().toISOString(),
    ip: alert.ip || 'unknown',
    type: alert.type || 'unknown',
    severity: alert.severity || 'Low',
    status: 'New',
    description: alert.description || 'No description available.',
  }));
}

function buildAttackTypeDistribution(alerts = []) {
  const counts = alerts.reduce((acc, alert) => {
    const key = alert.type || 'unknown';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts).map(([type, count]) => ({ type, count }));
}

function Dashboard({ onSyncTick }) {
  const [interval, setIntervalValue] = useState('24h');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [uploadDrivenState, setUploadDrivenState] = useState(false);
  const [payload, setPayload] = useState({
    stats: null,
    severity_distribution: { Critical: 0, High: 0, Medium: 0, Low: 0 },
    attack_timeline: [],
    attack_types: [],
    top_attacking_ips: [],
    geo_sources: [],
    recent_alerts: [],
  });

  const loadDashboard = useCallback(async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const data = await api.getDashboard(interval);
      setPayload(data);
      setError('');
      onSyncTick?.();
    } catch (err) {
      setError(err.message);
    } finally {
      if (isFirst) setLoading(false);
    }
  }, [interval, onSyncTick]);

  useEffect(() => {
    if (uploadDrivenState) return;
    loadDashboard(true);
    const timer = setInterval(() => loadDashboard(false), 5000);
    return () => clearInterval(timer);
  }, [loadDashboard, uploadDrivenState]);

  const attackTypeData = useMemo(
    () => payload.attack_types.map((item) => ({ name: item.type, value: item.count })),
    [payload.attack_types]
  );

  const severityData = useMemo(
    () => Object.entries(payload.severity_distribution).map(([name, value]) => ({ name, value })),
    [payload.severity_distribution]
  );

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError('');
      const response = await api.uploadLog(file);

      const mappedAlerts = mapAlerts(response.alerts || []);
      setPayload((prev) => ({
        ...prev,
        stats: {
          total_events: Number(response.total_events || 0),
          windows_events: prev.stats?.windows_events || 0,
          syslog_events: prev.stats?.syslog_events || 0,
          all_devices: prev.stats?.all_devices || 0,
        },
        severity_distribution: mapSeverityToDashboard(response.severity),
        top_attacking_ips: mapTopIps(response.top_ips || []),
        recent_alerts: mappedAlerts.slice(0, 8),
        attack_types: buildAttackTypeDistribution(mappedAlerts),
      }));

      setUploadDrivenState(true);
      setMessage(
        `Processed ${file.name}: ${response.total_events || 0} total events, ${mappedAlerts.length} alerts tracked.`
      );
      setTimeout(() => setMessage(''), 4000);
    } catch (err) {
      setError(err.message);
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
          <select className="soc-input" value={interval} onChange={(e) => setIntervalValue(e.target.value)}>
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
            <StatCard title="Total Events" value={payload.stats?.total_events} accent="#3b82f6" subtitle="Collected logs" />
            <StatCard title="Windows Events" value={payload.stats?.windows_events} accent="#2ecc71" subtitle="Endpoint telemetry" />
            <StatCard title="Syslog Events" value={payload.stats?.syslog_events} accent="#ffd60a" subtitle="Network / Linux logs" />
            <StatCard title="Devices" value={payload.stats?.all_devices} accent="#ff8c00" subtitle="Active assets" />
          </>
        )}
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <EventChart data={payload.attack_timeline} />
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

        <TopAttackingIps ips={payload.top_attacking_ips} />
        <GeoThreatMap geoSources={payload.geo_sources} />
      </section>

      <section className="soc-card p-4">
        <h3 className="text-sm font-semibold text-soc-text">Recent Alerts</h3>
        <div className="mt-3 grid gap-2 lg:grid-cols-2">
          {payload.recent_alerts.length === 0 ? (
            <p className="text-sm text-soc-muted">No alerts in selected time window.</p>
          ) : (
            payload.recent_alerts.map((alert) => (
              <div key={alert.id} className="rounded-xl border border-soc-border bg-soc-panelSoft/55 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-soc-text">{alert.type}</p>
                  <span className="text-xs" style={{ color: SEVERITY_COLORS[alert.severity] }}>
                    {alert.severity}
                  </span>
                </div>
                <p className="mt-1 text-xs text-soc-muted">{alert.ip} • {new Date(alert.timestamp).toLocaleString()}</p>
                <p className="mt-1 text-xs text-soc-muted">{alert.description}</p>
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
