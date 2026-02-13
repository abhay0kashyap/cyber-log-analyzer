import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

function EventChart({ data, title = 'Attack Timeline' }) {
  return (
    <section className="soc-card h-80 p-4">
      <h3 className="mb-3 text-sm font-semibold text-soc-text">{title}</h3>
      <ResponsiveContainer width="100%" height="90%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="timelineFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#25304a" strokeDasharray="3 4" />
          <XAxis dataKey="time" stroke="#91a0bf" minTickGap={24} />
          <YAxis stroke="#91a0bf" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#10182b',
              border: '1px solid #25304a',
              borderRadius: 10,
              color: '#e6edf8',
            }}
          />
          <Area type="monotone" dataKey="alerts" stroke="#3b82f6" strokeWidth={2.3} fill="url(#timelineFill)" />
        </AreaChart>
      </ResponsiveContainer>
    </section>
  );
}

export default EventChart;
