import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { SEVERITY_BADGES, STATUS_BADGES } from '../utils/severity';

function AlertDetailModal({ data, onClose }) {
  if (!data) return null;

  const { alert, risk_score: riskScore, high_risk: highRisk, related_logs: logs, related_alerts: alerts, activity_timeline: timeline } = data;

  return (
    <div className="fixed inset-0 z-40 flex items-start justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="soc-card max-h-[90vh] w-full max-w-5xl overflow-y-auto p-5">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-soc-text">Alert #{alert.id}</h3>
            <p className="text-xs text-soc-muted">{new Date(alert.timestamp).toLocaleString()} • {alert.ip}</p>
          </div>
          <button className="soc-button" onClick={onClose} type="button">
            Close
          </button>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <div className="soc-card bg-soc-panelSoft/60 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Type</p>
            <p className="mt-1 text-sm font-semibold text-soc-text">{alert.type}</p>
          </div>
          <div className="soc-card bg-soc-panelSoft/60 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Severity / Status</p>
            <div className="mt-2 flex gap-2">
              <span className={`soc-badge ${SEVERITY_BADGES[alert.severity]}`}>{alert.severity}</span>
              <span className={`soc-badge ${STATUS_BADGES[alert.status]}`}>{alert.status}</span>
            </div>
          </div>
          <div className="soc-card bg-soc-panelSoft/60 p-4">
            <p className="text-xs uppercase tracking-[0.12em] text-soc-muted">Risk Score</p>
            <p className="mt-1 text-xl font-bold text-soc-text">{riskScore}</p>
            {highRisk ? <span className="mt-1 inline-block text-xs text-[#ffb35a]">🔥 HIGH RISK</span> : null}
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <section className="soc-card p-4">
            <h4 className="text-sm font-semibold text-soc-text">Timeline of Activity</h4>
            <div className="mt-2 h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeline}>
                  <XAxis dataKey="time" hide />
                  <YAxis stroke="#91a0bf" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#10182b',
                      border: '1px solid #25304a',
                      borderRadius: 10,
                    }}
                  />
                  <Area type="monotone" dataKey="events" stroke="#3b82f6" fill="#3b82f633" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="soc-card p-4">
            <h4 className="text-sm font-semibold text-soc-text">Related Alerts (same IP)</h4>
            <div className="mt-2 space-y-2">
              {alerts.slice(0, 6).map((item) => (
                <div key={item.id} className="rounded-lg border border-soc-border bg-soc-panelSoft/60 p-2 text-xs">
                  <p className="font-semibold text-soc-text">{item.type}</p>
                  <p className="text-soc-muted">{new Date(item.timestamp).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="mt-4 soc-card p-4">
          <h4 className="text-sm font-semibold text-soc-text">Related Logs ({logs.length})</h4>
          <div className="mt-2 max-h-56 space-y-2 overflow-y-auto">
            {logs.slice(0, 20).map((entry) => (
              <div key={entry.id} className="rounded-lg border border-soc-border bg-soc-panelSoft/50 p-2 text-xs text-soc-muted">
                <p>
                  <span className="text-soc-text">{new Date(entry.timestamp).toLocaleString()}</span> • {entry.event_type} •{' '}
                  {entry.status}
                </p>
                <p className="mt-1 break-all">{entry.raw}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default AlertDetailModal;
