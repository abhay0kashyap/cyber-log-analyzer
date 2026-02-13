function GeoThreatMap({ geoSources }) {
  return (
    <section className="soc-card p-4">
      <h3 className="text-sm font-semibold text-soc-text">Geo Threat Feed (Mocked)</h3>
      <div className="mt-3 space-y-2">
        {geoSources.length === 0 ? (
          <p className="text-sm text-soc-muted">No geolocation records.</p>
        ) : (
          geoSources.map((entry) => (
            <div key={`${entry.ip}-${entry.country}`} className="rounded-xl border border-soc-border bg-soc-panelSoft/55 p-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-soc-text">{entry.country} • {entry.city}</p>
                <span className="text-xs text-soc-muted">Score {entry.attack_score}</span>
              </div>
              <p className="mt-1 text-xs text-soc-muted">
                {entry.ip} • {entry.lat.toFixed(2)}, {entry.lng.toFixed(2)}
              </p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default GeoThreatMap;
