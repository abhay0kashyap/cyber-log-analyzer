import { useCallback, useEffect, useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import { api } from '../services/api';
import { buildCsvFilename, downloadTextFile, logsToCsv } from '../utils/csvExport';
import { SEVERITY_COLORS } from '../utils/severity';

const RANGE_OPTIONS = [
  { value: 'all', label: 'All time' },
  { value: '1h', label: 'Last 1 hour' },
  { value: '24h', label: 'Last 24 hours' },
  { value: 'week', label: 'Last 7 days' },
];

function Alerts({ onSyncTick }) {
  const [range, setRange] = useState('all');
  const [severity, setSeverity] = useState('');
  const [query, setQuery] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exportNotice, setExportNotice] = useState('');

  const loadAlerts = useCallback(async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const payload = await api.getSocAlerts(range);
      setAlerts(payload.alerts || []);
      setError('');
      onSyncTick?.();
    } catch (err) {
      console.error('Failed to load alerts', err);
      setError(err.message || 'Failed to load alerts');
    } finally {
      if (isFirst) setLoading(false);
    }
  }, [onSyncTick, range]);

  useEffect(() => {
    loadAlerts(true);
  }, [loadAlerts]);

  const filteredAlerts = useMemo(() => {
    const q = query.trim().toLowerCase();
    return alerts.filter((alert) => {
      const severityMatch = !severity || alert.severity === severity;
      const textMatch =
        !q ||
        alert.ip?.toLowerCase().includes(q) ||
        alert.type?.toLowerCase().includes(q) ||
        alert.message?.toLowerCase().includes(q);
      return severityMatch && textMatch;
    });
  }, [alerts, query, severity]);

  const severityCounts = useMemo(() => {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    for (const alert of filteredAlerts) {
      if (counts[alert.severity] != null) {
        counts[alert.severity] += 1;
      }
    }
    return counts;
  }, [filteredAlerts]);

  const severityPieData = useMemo(
    () => Object.entries(severityCounts).map(([name, value]) => ({ name, value })),
    [severityCounts]
  );

  const exportRows = useMemo(
    () =>
      filteredAlerts.map((alert) => ({
        timestamp: alert.timestamp,
        ip: alert.ip,
        severity: alert.severity,
        message: alert.message || '',
      })),
    [filteredAlerts]
  );

  const handleExportCsv = () => {
    if (!exportRows.length) return;
    const csv = logsToCsv(exportRows);
    const filename = buildCsvFilename();
    downloadTextFile(csv, filename);
    const note = `Exported ${exportRows.length} alerts to ${filename}`;
    setExportNotice(note);
    console.info(note);
  };

  useEffect(() => {
    if (!exportNotice) return;
    const timer = window.setTimeout(() => setExportNotice(''), 2500);
    return () => window.clearTimeout(timer);
  }, [exportNotice]);

  return (
    <div className="space-y-4">
      <section className="soc-card p-4">
        <div className="grid gap-3 md:grid-cols-4">
          <label className="text-xs text-soc-muted">
            Range
            <select className="soc-input mt-1 w-full" value={range} onChange={(e) => setRange(e.target.value)}>
              {RANGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>

          <label className="text-xs text-soc-muted">
            Severity
            <select className="soc-input mt-1 w-full" value={severity} onChange={(e) => setSeverity(e.target.value)}>
              <option value="">All</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </label>

          <label className="text-xs text-soc-muted md:col-span-2">
            Search
            <input
              className="soc-input mt-1 w-full"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by IP, type, or message"
            />
          </label>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <section className="soc-card p-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-soc-text">Severity Counts</h3>
          <div className="mt-3 grid gap-2 sm:grid-cols-4">
            {Object.entries(severityCounts).map(([name, value]) => (
              <div key={name} className="rounded-lg border border-soc-border bg-soc-panelSoft/60 px-3 py-2">
                <p className="text-xs text-soc-muted">{name}</p>
                <p className="text-xl font-bold" style={{ color: SEVERITY_COLORS[name] }}>{value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="soc-card h-52 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={severityPieData} dataKey="value" nameKey="name" outerRadius={70}>
                {severityPieData.map((entry) => (
                  <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </section>
      </section>

      <section className="soc-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-soc-panelSoft/80 text-xs uppercase tracking-[0.12em] text-soc-muted">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">IP</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Message</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td className="px-4 py-8 text-center text-soc-muted" colSpan={5}>Loading alerts...</td>
                </tr>
              ) : filteredAlerts.length === 0 ? (
                <tr>
                  <td className="px-4 py-8 text-center text-soc-muted" colSpan={5}>No alerts found for current filters.</td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => (
                  <tr key={alert.id} className="border-t border-soc-border hover:bg-soc-panelSoft/45">
                    <td className="px-4 py-3 text-soc-muted">{new Date(alert.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3 font-medium text-soc-text">{alert.ip}</td>
                    <td className="px-4 py-3 text-soc-text">{alert.type}</td>
                    <td className="px-4 py-3">
                      <span className="soc-badge border border-soc-border bg-soc-panelSoft/70">{alert.severity}</span>
                    </td>
                    <td className="px-4 py-3 text-soc-muted">{alert.message}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="flex flex-wrap gap-2">
        <button className="soc-button py-1" onClick={handleExportCsv} disabled={exportRows.length === 0} type="button">
          Export CSV
        </button>
      </section>

      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
      {exportNotice ? <p className="text-sm text-[#7ce38b]">{exportNotice}</p> : null}
    </div>
  );
}

export default Alerts;
