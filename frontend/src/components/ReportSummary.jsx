import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { SEVERITY_COLORS } from '../utils/severity';

function ReportSummary({ report }) {
  if (!report) {
    return <section className="soc-card p-5 text-sm text-soc-muted">Generate a report to view analytics.</section>;
  }

  const severityData = Object.entries(report.severity_distribution).map(([name, value]) => ({ name, value }));

  return (
    <section className="grid gap-4 xl:grid-cols-3">
      <div className="soc-card h-80 p-4">
        <h3 className="text-sm font-semibold text-soc-text">Severity Distribution</h3>
        <div className="mt-2 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={severityData} dataKey="value" nameKey="name" outerRadius={90}>
                {severityData.map((entry) => (
                  <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="soc-card h-80 p-4">
        <h3 className="text-sm font-semibold text-soc-text">Attack Type Distribution</h3>
        <div className="mt-2 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={report.attack_types || []}>
              <XAxis dataKey="type" hide />
              <YAxis stroke="#91a0bf" />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="soc-card h-80 p-4">
        <h3 className="text-sm font-semibold text-soc-text">Top IP Sources</h3>
        <div className="mt-3 space-y-2">
          {(report.top_ip_sources || []).slice(0, 8).map((item) => (
            <div key={item.ip} className="rounded-lg border border-soc-border bg-soc-panelSoft/50 p-2 text-xs">
              <p className="font-medium text-soc-text">{item.ip}</p>
              <p className="text-soc-muted">Alerts: {item.count} • Score: {item.attack_score}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ReportSummary;
