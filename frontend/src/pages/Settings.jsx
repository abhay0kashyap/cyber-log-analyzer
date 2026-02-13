import { useEffect, useState } from 'react';

import ThresholdEditor from '../components/ThresholdEditor';
import { api } from '../services/api';

const initialState = {
  brute_force_count: 10,
  repeated_failed_threshold: 5,
  unknown_ip_spike_threshold: 15,
  live_monitoring: true,
};

function Settings() {
  const [settings, setSettings] = useState(initialState);
  const [apiStatus, setApiStatus] = useState('checking');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [health, payload] = await Promise.all([api.getHealth(), api.getSettings()]);
      setApiStatus(health.status === 'ok' ? 'online' : 'offline');
      setSettings(payload);
      setError('');
    } catch (err) {
      setApiStatus('offline');
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const save = async () => {
    try {
      setSaving(true);
      const updated = await api.saveSettings(settings);
      setSettings(updated);
      setMessage('Configuration saved. Detection engine updated.');
      setTimeout(() => setMessage(''), 2800);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <ThresholdEditor
        values={settings}
        saving={saving}
        onChange={(key, value) => setSettings((prev) => ({ ...prev, [key]: value }))}
        onSave={save}
      />

      <section className="soc-card space-y-3 p-4">
        <h3 className="text-sm font-semibold text-soc-text">Runtime Controls</h3>
        <div className="flex items-center justify-between rounded-xl border border-soc-border bg-soc-panelSoft/55 px-3 py-2 text-sm">
          <span className="text-soc-muted">API Status</span>
          <span className={`soc-badge ${apiStatus === 'online' ? 'border border-[#2ecc71]/50 bg-[#2ecc71]/20 text-[#76e3ac]' : 'border border-[#ff3b3b]/50 bg-[#ff3b3b]/20 text-[#ff7f7f]'}`}>
            {apiStatus}
          </span>
        </div>

        <label className="flex items-center justify-between rounded-xl border border-soc-border bg-soc-panelSoft/55 px-3 py-2 text-sm">
          <span className="text-soc-muted">Live monitoring</span>
          <input
            type="checkbox"
            checked={settings.live_monitoring}
            onChange={(e) => setSettings((prev) => ({ ...prev, live_monitoring: e.target.checked }))}
          />
        </label>
      </section>

      {message ? <p className="text-sm text-blue-300">{message}</p> : null}
      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
    </div>
  );
}

export default Settings;
