import { useMemo } from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Area,
} from "recharts";

interface SpectrogramProps {
  isActive: boolean;
  hasAnomaly: boolean;
  rms?: number;
  rmsHistory?: Array<{ time: string; rms: number }>;
  msgCount?: number;
}

export function Spectrogram({
  isActive,
  hasAnomaly,
  rms = 0,
  rmsHistory = [],
  msgCount = 0,
}: SpectrogramProps) {
  const visibleData = rmsHistory.slice(-150);

  const yMax =
    visibleData.length > 0
      ? Math.max(...visibleData.map((d) => d.rms), 0.01) * 1.25
      : 0.01;

  // Determine current trend color based on last two points
  const lineColor = useMemo(() => {
    if (visibleData.length < 2) return "#89b4fa";
    const last = visibleData[visibleData.length - 1];
    const prev = visibleData[visibleData.length - 2];
    if (last.rms > prev.rms * 1.02) return "#f38ba8"; // rising — red
    if (last.rms < prev.rms * 0.98) return "#89b4fa"; // falling — blue
    return "#a6e3a1";                                   // stable  — green
  }, [visibleData]);

  return (
    <div
      className="border border-[#313244] rounded-lg p-4 h-full flex flex-col"
      style={{ backgroundColor: "#1e1e2e" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div
            className="text-sm font-bold tracking-tight"
            style={{ color: "#cdd6f4" }}
          >
            Resonance — Live RMS Monitor
          </div>
          <div
            className="flex items-center gap-2 text-xs"
            style={{ fontFamily: "monospace" }}
          >
            <span style={{ color: "#f38ba8" }}>▲ rising</span>
            <span style={{ color: "#a6e3a1" }}>● stable</span>
            <span style={{ color: "#89b4fa" }}>▼ falling</span>
          </div>
        </div>
        <div
          className="text-xs"
          style={{ color: "#a6adc8", fontFamily: "monospace" }}
        >
          msgs: {String(msgCount).padStart(6, "\u2007")}{"   "}rms:{" "}
          <span style={{ color: lineColor, fontWeight: "bold" }}>
            {rms.toFixed(6)}
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={visibleData}
            margin={{ top: 4, right: 8, left: -10, bottom: 4 }}
          >
            <defs>
              <linearGradient id="rmsAreaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={lineColor} stopOpacity={0.18} />
                <stop offset="95%" stopColor={lineColor} stopOpacity={0.01} />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="#313244"
              strokeWidth={0.5}
              strokeOpacity={0.6}
            />
            <XAxis
              dataKey="time"
              stroke="#313244"
              tick={{ fill: "#6c7086", fontSize: 10, fontFamily: "monospace" }}
              tickLine={{ stroke: "#313244" }}
              interval={Math.floor(visibleData.length / 6) || 1}
              minTickGap={40}
            />
            <YAxis
              stroke="#313244"
              tick={{ fill: "#6c7086", fontSize: 10, fontFamily: "monospace" }}
              tickLine={{ stroke: "#313244" }}
              domain={[0, yMax]}
              tickFormatter={(v: number) => v.toFixed(3)}
              width={50}
            />

            {/* Subtle area fill under the line */}
            <Area
              type="monotone"
              dataKey="rms"
              stroke="none"
              fill="url(#rmsAreaGradient)"
              isAnimationActive={false}
            />

            {/* Main line — color reflects current trend */}
            <Line
              type="monotone"
              dataKey="rms"
              stroke={lineColor}
              strokeWidth={1.6}
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Footer labels */}
      <div className="flex items-center justify-between mt-1 px-1">
        <div
          className="text-xs"
          style={{ color: "#a6adc8", fontFamily: "monospace" }}
        >
          RMS ↑
        </div>
        <div
          className="text-xs"
          style={{ color: "#a6adc8", fontFamily: "monospace" }}
        >
          Time (s) →
        </div>
      </div>
    </div>
  );
}