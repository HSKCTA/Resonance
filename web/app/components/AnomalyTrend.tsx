import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, ReferenceLine } from "recharts";

interface AnomalyTrendProps {
  data: Array<{ time: string; score: number }>;
  threshold: number;
}

export function AnomalyTrend({ data, threshold }: AnomalyTrendProps) {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded p-4">
      <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
        ANOMALY TREND — LAST 15 MINUTES
      </div>
      
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" opacity={0.5} />
          <XAxis 
            dataKey="time" 
            stroke="#475569"
            style={{ fontSize: "11px", fontFamily: 'Inter, sans-serif' }}
            tick={{ fill: "#64748B" }}
            tickLine={{ stroke: "#1E293B" }}
          />
          <YAxis 
            stroke="#475569"
            style={{ fontSize: "11px", fontFamily: 'Inter, sans-serif' }}
            tick={{ fill: "#64748B" }}
            tickLine={{ stroke: "#1E293B" }}
            domain={[0, 1]}
          />
          <ReferenceLine 
            y={threshold} 
            stroke="#ef4444" 
            strokeDasharray="4 4"
            strokeWidth={1}
            opacity={0.5}
          />
          <Line 
            type="monotone" 
            dataKey="score" 
            stroke="#3B82F6" 
            strokeWidth={1.5}
            dot={false}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-3 flex items-center justify-between text-xs" style={{ fontFamily: 'Inter, sans-serif' }}>
        <div className="text-[#64748B]">
          Baseline: <span className="text-[#94A3B8] font-medium">0.050</span>
        </div>
        <div className="text-[#64748B]">
          Threshold: <span className="text-[#94A3B8] font-medium">{threshold.toFixed(3)}</span>
        </div>
      </div>
    </div>
  );
}
