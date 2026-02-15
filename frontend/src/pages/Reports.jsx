import { useCallback, useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { api } from '../services/api';
import { SEVERITY_COLORS } from '../utils/severity';

const RANGE_OPTIONS = [
  { value: '1h', label: 'Last 1 hour' },
  { value: '24h', label: 'Last 24 hours' },
  { value: 'week', label: 'Last 7 days' },
];

function Reports() {
  const [range, setRange] = useState('24h');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadReport = useCallback(async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const payload = await api.getSocReport(range);
      setReport(payload);
      setError('');
    } catch (err) {
      console.error('Failed to load report', err);
      setError(err.message || 'Failed to load report');
    } finally {
      if (isFirst) setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    loadReport(true);
  }, [loadReport]);

  const severityData = useMemo(() => {
    if (!report) return [];
    return [
      { name: 'Critical', value: Number(report.severity_distribution?.critical || 0) },
      { name: 'High', value: Number(report.severity_distribution?.high || 0) },
      { name: 'Medium', value: Number(report.severity_distribution?.medium || 0) },
      { name: 'Low', value: Number(report.severity_distribution?.low || 0) },
    ];
  }, [report]);

  return (
    <div className="space-y-4">
      <section className="soc-card flex flex-wrap items-center gap-2 p-4">
        <select className="soc-input" value={range} onChange={(e) => setRange(e.target.value)}>
          {RANGE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
        <button className="soc-button" onClick={() => loadReport(false)} type="button" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Report'}
        </button>
      </section>

      {loading ? (
        <section className="soc-card p-6 text-sm text-soc-muted">Loading report...</section>
      ) : report ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="soc-card p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Total Events</p>
              <p className="mt-2 text-2xl font-bold text-soc-text">{report.total_events}</p>
            </div>
            <div className="soc-card p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Critical</p>
              <p className="mt-2 text-2xl font-bold" style={{ color: SEVERITY_COLORS.Critical }}>
                {report.severity_distribution?.critical || 0}
              </p>
            </div>
            <div className="soc-card p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">High</p>
              <p className="mt-2 text-2xl font-bold" style={{ color: SEVERITY_COLORS.High }}>
                {report.severity_distribution?.high || 0}
              </p>
            </div>
            <div className="soc-card p-4">
              <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Medium / Low</p>
              <p className="mt-2 text-2xl font-bold text-soc-text">
                {(report.severity_distribution?.medium || 0) + (report.severity_distribution?.low || 0)}
              </p>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            <section className="soc-card h-80 p-4">
              <h3 className="text-sm font-semibold text-soc-text">Severity Distribution</h3>
              <div className="mt-2 h-[88%]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={severityData} dataKey="value" nameKey="name" outerRadius={92}>
                      {severityData.map((entry) => (
                        <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="soc-card h-80 p-4">
              <h3 className="text-sm font-semibold text-soc-text">Top Attacking IPs</h3>
              <div className="mt-2 h-[88%]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={report.top_ips || []}>
                    <XAxis dataKey="ip" hide />
                    <YAxis stroke="#91a0bf" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </section>

          <section className="soc-card p-4">
            <h3 className="text-sm font-semibold text-soc-text">Top IP Details</h3>
            <div className="mt-3 space-y-2">
              {(report.top_ips || []).length === 0 ? (
                <p className="text-sm text-soc-muted">No IP activity in selected range.</p>
              ) : (
                (report.top_ips || []).map((item) => (
                  <div key={item.ip} className="rounded-lg border border-soc-border bg-soc-panelSoft/50 p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-soc-text">{item.ip}</p>
                      <p className="text-soc-muted">Events: {item.count}</p>
                    </div>
                    <p className="mt-1 text-xs text-soc-muted">Alert matches: {item.alert_count}</p>
                  </div>
                ))
              )}
            </div>
          </section>
        </>
      ) : (
        <section className="soc-card p-6 text-sm text-soc-muted">No report data available.</section>
      )}

      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
    </div>
  );
}

export default Reports;
