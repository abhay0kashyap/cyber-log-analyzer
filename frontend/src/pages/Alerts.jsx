import { useCallback, useEffect, useMemo, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import AlertDetailModal from '../components/AlertDetailModal';
import AlertTable from '../components/AlertTable';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { api } from '../services/api';
import { SEVERITY_COLORS } from '../utils/severity';

function Alerts({ onSyncTick }) {
  const [severity, setSeverity] = useState('');
  const [status, setStatus] = useState('');
  const [ipFilter, setIpFilter] = useState('');
  const debouncedIpFilter = useDebouncedValue(ipFilter, 350);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);

  const [data, setData] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: 15,
    total_pages: 1,
    severity_counts: { Critical: 0, High: 0, Medium: 0, Low: 0 },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyAlertId, setBusyAlertId] = useState(null);
  const [details, setDetails] = useState(null);
  const [detailsError, setDetailsError] = useState('');

  const loadAlerts = useCallback(async (isFirst = false) => {
    try {
      if (isFirst) setLoading(true);
      const payload = await api.getAlerts({
        page,
        page_size: pageSize,
        severity: severity || undefined,
        status: status || undefined,
        ip: debouncedIpFilter || undefined,
        q: debouncedIpFilter || undefined,
      });
      setData(payload);
      setError('');
      onSyncTick?.();
    } catch (err) {
      setError(err.message);
    } finally {
      if (isFirst) setLoading(false);
    }
  }, [debouncedIpFilter, onSyncTick, page, pageSize, severity, status]);

  useEffect(() => {
    loadAlerts(true);
  }, [loadAlerts]);

  useEffect(() => {
    const timer = setInterval(() => loadAlerts(false), 5000);
    return () => clearInterval(timer);
  }, [loadAlerts]);

  useEffect(() => {
    setPage(1);
  }, [severity, status, debouncedIpFilter, pageSize]);

  const severityPieData = useMemo(
    () => Object.entries(data.severity_counts || {}).map(([name, value]) => ({ name, value })),
    [data.severity_counts]
  );

  const openDetails = async (alertId) => {
    try {
      const payload = await api.getAlertDetails(alertId);
      setDetails(payload);
      setDetailsError('');
    } catch (err) {
      setDetailsError(err.message);
    }
  };

  const updateStatus = async (alertId, newStatus) => {
    try {
      setBusyAlertId(alertId);
      await api.updateAlertStatus(alertId, newStatus);
      await loadAlerts(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyAlertId(null);
    }
  };

  const blockIp = async (alertId) => {
    try {
      setBusyAlertId(alertId);
      await api.blockAlert(alertId);
      await loadAlerts(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyAlertId(null);
    }
  };

  return (
    <div className="space-y-4">
      <section className="soc-card p-4">
        <div className="grid gap-3 md:grid-cols-4">
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

          <label className="text-xs text-soc-muted">
            Alert Status
            <select className="soc-input mt-1 w-full" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All</option>
              <option value="New">New</option>
              <option value="Investigating">Investigating</option>
              <option value="Resolved">Resolved</option>
            </select>
          </label>

          <label className="text-xs text-soc-muted md:col-span-2">
            Search IP / Text
            <input
              className="soc-input mt-1 w-full"
              value={ipFilter}
              onChange={(e) => setIpFilter(e.target.value)}
              placeholder="Search IP or keywords"
            />
          </label>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <section className="soc-card p-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-soc-text">Severity Counts (Filtered)</h3>
          <div className="mt-3 grid gap-2 sm:grid-cols-4">
            {Object.entries(data.severity_counts).map(([name, value]) => (
              <div key={name} className="rounded-lg border border-soc-border bg-soc-panelSoft/60 px-3 py-2">
                <p className="text-xs text-soc-muted">{name}</p>
                <p className="text-xl font-bold" style={{ color: SEVERITY_COLORS[name] }}>
                  {value}
                </p>
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

      <AlertTable
        alerts={data.items}
        loading={loading}
        page={data.page}
        total={data.total}
        totalPages={data.total_pages}
        onPageChange={(nextPage) => setPage(nextPage)}
        onOpenDetails={openDetails}
        onStatusChange={updateStatus}
        onBlock={blockIp}
        busyAlertId={busyAlertId}
      />

      <section className="flex flex-wrap gap-2">
        <label className="text-xs text-soc-muted">
          Page Size
          <select className="soc-input ml-2" value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </label>
      </section>

      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
      {detailsError ? <p className="text-sm text-[#ff6a6a]">{detailsError}</p> : null}

      <AlertDetailModal data={details} onClose={() => setDetails(null)} />
    </div>
  );
}

export default Alerts;
