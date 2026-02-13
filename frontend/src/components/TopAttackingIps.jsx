function TopAttackingIps({ ips }) {
  return (
    <section className="soc-card p-4">
      <h3 className="text-sm font-semibold text-soc-text">Top Attacking IPs</h3>
      <div className="mt-3 space-y-2">
        {ips.length === 0 ? (
          <p className="text-sm text-soc-muted">No attack activity in last 10 minutes.</p>
        ) : (
          ips.map((item) => (
            <div key={item.ip} className="rounded-xl border border-soc-border bg-soc-panelSoft/50 p-3">
              <div className="flex items-center justify-between">
                <p className="font-medium text-soc-text">{item.ip}</p>
                <span className="soc-badge bg-blue-500/20 text-blue-300 border border-blue-400/30">
                  Score {item.attack_score}
                </span>
              </div>
              <p className="mt-1 text-xs text-soc-muted">
                Critical: {item.critical_count} • High: {item.high_count}
              </p>
              {item.high_risk ? <p className="mt-1 text-xs text-[#ffb35a]">🔥 HIGH RISK</p> : null}
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default TopAttackingIps;
