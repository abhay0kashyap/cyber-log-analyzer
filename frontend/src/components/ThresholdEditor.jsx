function ThresholdEditor({ values, onChange, onSave, saving }) {
  return (
    <section className="soc-card p-4">
      <h3 className="text-sm font-semibold text-soc-text">Detection Threshold Rules</h3>
      <div className="mt-3 grid gap-3 lg:grid-cols-3">
        <label className="text-sm">
          <span className="mb-1 block text-soc-muted">Brute force count</span>
          <input
            className="soc-input w-full"
            type="number"
            min="1"
            value={values.brute_force_count}
            onChange={(e) => onChange('brute_force_count', Number(e.target.value) || 1)}
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-soc-muted">Failed login threshold</span>
          <input
            className="soc-input w-full"
            type="number"
            min="1"
            value={values.repeated_failed_threshold}
            onChange={(e) => onChange('repeated_failed_threshold', Number(e.target.value) || 1)}
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-soc-muted">Unknown IP spike threshold</span>
          <input
            className="soc-input w-full"
            type="number"
            min="1"
            value={values.unknown_ip_spike_threshold}
            onChange={(e) => onChange('unknown_ip_spike_threshold', Number(e.target.value) || 1)}
          />
        </label>
      </div>
      <button type="button" onClick={onSave} disabled={saving} className="soc-button mt-4 border-blue-400/40 text-blue-300">
        {saving ? 'Saving...' : 'Save Thresholds'}
      </button>
    </section>
  );
}

export default ThresholdEditor;
