import { useState } from 'react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import ReportSummary from '../components/ReportSummary';
import { api } from '../services/api';

function Reports() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateReport = async () => {
    try {
      setLoading(true);
      const payload = await api.getReport();
      setReport(payload);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = href;
    anchor.download = `soc-report-${new Date().toISOString().replaceAll(':', '_')}.json`;
    anchor.click();
    URL.revokeObjectURL(href);
  };

  const downloadCsv = async () => {
    try {
      const blob = await api.downloadReportCsv();
      const href = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = href;
      anchor.download = `soc-report-${new Date().toISOString().slice(0, 10)}.csv`;
      anchor.click();
      URL.revokeObjectURL(href);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-4">
      <section className="soc-card flex flex-wrap gap-2 p-4">
        <button className="soc-button border-blue-400/50 text-blue-300" onClick={generateReport} type="button" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
        <button className="soc-button" onClick={downloadJson} type="button" disabled={!report}>
          Download JSON
        </button>
        <button className="soc-button" onClick={downloadCsv} type="button" disabled={!report}>
          Download CSV
        </button>
      </section>

      {report ? (
        <>
          <section className="soc-card h-80 p-4">
            <h3 className="text-sm font-semibold text-soc-text">Events Over Time</h3>
            <div className="mt-2 h-[88%]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={report.events_over_time}>
                  <XAxis dataKey="time" hide />
                  <YAxis stroke="#91a0bf" />
                  <Tooltip />
                  <Area dataKey="events" type="monotone" stroke="#3b82f6" fill="#3b82f633" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          <ReportSummary report={report} />
        </>
      ) : (
        <section className="soc-card p-6 text-sm text-soc-muted">Run report generation to view export analytics.</section>
      )}

      {error ? <p className="text-sm text-[#ff6a6a]">{error}</p> : null}
    </div>
  );
}

export default Reports;
