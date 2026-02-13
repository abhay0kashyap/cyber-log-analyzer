function StatCard({ title, value, accent = '#3b82f6', subtitle }) {
  return (
    <article className="soc-card animate-in px-4 py-4">
      <p className="text-xs uppercase tracking-[0.14em] text-soc-muted">{title}</p>
      <p className="mt-2 text-3xl font-bold leading-none text-soc-text">{Number(value || 0).toLocaleString()}</p>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-soc-muted">{subtitle || 'Live telemetry'}</span>
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: accent }} />
      </div>
    </article>
  );
}

export default StatCard;
