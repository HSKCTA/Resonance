import { useState, useEffect } from "react";
import { useResonanceData } from "./hooks/useResonanceData";
import { HeaderBar } from "./components/HeaderBar";
import { NodeList } from "./components/NodeList";
import { HealthScore } from "./components/HealthScore";
import { AnomalyTrend } from "./components/AnomalyTrend";
import { HarmonicAnalysis } from "./components/HarmonicAnalysis";
import { AMDStats } from "./components/AMDStats";
import { PipelineLatency } from "./components/PipelineLatency";
import { FaultExplanation } from "./components/FaultExplanation";
import { Spectrogram } from "./components/Spectrogram";
import { SystemStats } from "./components/SystemStats";

interface Node {
  id: string;
  name: string;
  status: "healthy" | "warning" | "critical";
}

export default function App() {
  // ─── Live data from Node B via Socket.IO ───
  const live = useResonanceData();

  const [activeNode, setActiveNode] = useState("NODE 01");

  const threshold = 0.18;
  const hasAnomaly = live.severity !== "NORMAL";

  const nodes: Node[] = [
    {
      id: "NODE 01",
      name: "Compressor Bearing",
      status: activeNode === "NODE 01" ? live.status : "healthy",
    },
    {
      id: "NODE 02",
      name: "Motor Drive Unit",
      status: "healthy",
    },
    { id: "NODE 03", name: "Pump Assembly", status: "healthy" },
  ];

  // Derive harmonic levels from live severity/MSE
  const isHigh = live.severity === "HIGH";
  const isMediumPlus = live.severity === "MEDIUM" || live.severity === "HIGH";
  const isAnyAnomaly = live.severity !== "NORMAL";

  const harmonics = [
    {
      label: "1× RPM",
      frequency: 49,
      level: isHigh ? 0.82 : isAnyAnomaly ? 0.55 : 0.45,
      status: isHigh
        ? ("critical" as const)
        : isAnyAnomaly
          ? ("elevated" as const)
          : ("nominal" as const),
    },
    {
      label: "2× RPM",
      frequency: 98,
      level: isMediumPlus ? 0.88 : isAnyAnomaly ? 0.42 : 0.32,
      status: isMediumPlus
        ? ("elevated" as const)
        : ("nominal" as const),
    },
    {
      label: "3× RPM",
      frequency: 147,
      level: isHigh ? 0.65 : 0.15,
      status: isHigh
        ? ("elevated" as const)
        : ("nominal" as const),
    },
  ];

  const amdStats = {
    inference: "ONNX · CPU · ~4.7ms",
    backend: "ONNX Runtime (CPU)",
    activeNodes: live.connected ? 1 : 0,
    totalNodes: 3,
    framesPerSec: live.connected ? Math.round(live.msgCount / Math.max((Date.now() / 1000) % 3600, 1) * 2) || 2 : 0,
  };

  const pipelineLatency = {
    dsp: 23,
    ai: 5,
    alert: 30,
  };

  const systemStats = {
    sampleRate: "44.1 kHz",
    fftSize: "2048 pt",
    overlap: "75%",
    edgeDevice: "AMD Ryzen AI",
  };

  const faultExplanation = live.alert ? {
    en: live.alert,
    hi: live.alert,
    mr: live.alert,
  } : undefined;

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white" style={{ fontFamily: 'Inter, sans-serif' }}>
      <HeaderBar connected={live.connected} rms={live.rms} />

      <div className="flex h-[calc(100vh-3rem)]">
        <NodeList
          nodes={nodes}
          activeNode={activeNode}
          onSelectNode={setActiveNode}
        />

        <div className="flex-1 p-6 flex flex-col">
          {/* Main 3x2 Grid */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <HealthScore score={live.mse} status={live.status} />
            <AnomalyTrend
              data={live.trendData}
              threshold={threshold}
            />
            <HarmonicAnalysis harmonics={harmonics} />
            <AMDStats stats={amdStats} />
            <PipelineLatency latency={pipelineLatency} />
            <FaultExplanation
              hasAnomaly={hasAnomaly}
              score={live.mse}
              threshold={threshold}
              explanation={faultExplanation}
            />
          </div>

          {/* Full-width Spectrogram */}
          <div className="flex-1 min-h-0">
            <Spectrogram
              isActive={true}
              hasAnomaly={hasAnomaly}
              rms={live.rms}
              rmsHistory={live.rmsHistory}
              msgCount={live.msgCount}
            />
          </div>
        </div>

        <SystemStats stats={systemStats} />
      </div>
    </div>
  );
}