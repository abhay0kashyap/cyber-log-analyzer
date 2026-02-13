function Navbar({ lastUpdated }) {
  return (
    <header className="sticky top-0 z-20 border-b border-soc-border bg-[#0b1020]/90 px-4 py-3 backdrop-blur sm:px-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-soc-text">Security Operations Dashboard</h1>
          <p className="text-xs text-soc-muted">Real-time detection, triage, and incident correlation</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="rounded-lg border border-soc-border bg-soc-panelSoft px-3 py-1.5 text-xs text-soc-muted">
            Updated: {lastUpdated || '--'}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
