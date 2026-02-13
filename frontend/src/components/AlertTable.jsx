import { SEVERITY_BADGES, STATUS_BADGES } from '../utils/severity';

function AlertTable({
  alerts,
  loading,
  page,
  total,
  totalPages,
  onPageChange,
  onOpenDetails,
  onStatusChange,
  onBlock,
  busyAlertId,
}) {
  return (
    <section className="soc-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-soc-panelSoft/80 text-xs uppercase tracking-[0.12em] text-soc-muted">
            <tr>
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3">IP</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Risk</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td className="px-4 py-8 text-center text-soc-muted" colSpan={7}>
                  Loading alerts...
                </td>
              </tr>
            ) : alerts.length === 0 ? (
              <tr>
                <td className="px-4 py-8 text-center text-soc-muted" colSpan={7}>
                  No alerts for selected filters.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.id} className="border-t border-soc-border hover:bg-soc-panelSoft/45">
                  <td className="px-4 py-3 text-soc-muted">{new Date(alert.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-3 font-medium text-soc-text">{alert.ip}</td>
                  <td className="px-4 py-3 text-soc-text">{alert.type}</td>
                  <td className="px-4 py-3">
                    <span className={`soc-badge ${SEVERITY_BADGES[alert.severity]}`}>{alert.severity}</span>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={alert.status}
                      className={`soc-input py-1 ${STATUS_BADGES[alert.status] || ''}`}
                      onChange={(e) => onStatusChange(alert.id, e.target.value)}
                    >
                      <option value="New">New</option>
                      <option value="Investigating">Investigating</option>
                      <option value="Resolved">Resolved</option>
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-soc-muted">Score: {alert.risk_score}</span>
                      {alert.high_risk ? (
                        <span className="soc-badge border border-[#ff8c00]/50 bg-[#ff8c00]/20 text-[#ffc57a]">
                          🔥 HIGH RISK
                        </span>
                      ) : null}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button className="soc-button py-1" onClick={() => onOpenDetails(alert.id)} type="button">
                        Details
                      </button>
                      <button
                        className="soc-button py-1 text-[#ff8c00]"
                        onClick={() => onBlock(alert.id)}
                        disabled={busyAlertId === alert.id || alert.blocked}
                        type="button"
                      >
                        {alert.blocked ? 'Blocked' : busyAlertId === alert.id ? 'Blocking...' : 'Auto Block'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-soc-border px-4 py-3 text-xs text-soc-muted">
        <span>
          Page {page} / {totalPages} • {total} alerts
        </span>
        <div className="flex items-center gap-2">
          <button className="soc-button py-1" onClick={() => onPageChange(page - 1)} disabled={page <= 1} type="button">
            Prev
          </button>
          <button
            className="soc-button py-1"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            type="button"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}

export default AlertTable;
