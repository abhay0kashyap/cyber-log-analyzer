import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const LiveChart = ({ data }) => {
  return (
    <div style={{
      background: "#111827",
      padding: "20px",
      borderRadius: "12px",
      border: "1px solid #1e293b",
      boxShadow: "0 0 20px rgba(56, 189, 248, 0.3)",
      marginTop: "30px"
    }}>
      <h3 style={{ color: "#38bdf8", marginBottom: "20px" }}>
        Live Event Activity
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#1e293b" />
          <XAxis dataKey="time" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="events"
            stroke="#22d3ee"
            strokeWidth={3}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiveChart;
