interface AMDStatsProps {
  stats: {
    inference: string;
    backend: string;
    activeNodes: number;
    totalNodes: number;
    framesPerSec: number;
  };
}

export function AMDStats({ stats }: AMDStatsProps) {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded p-4">
      <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
        AMD SYSTEM STATS
      </div>

      <div className="space-y-3">
        <div className="flex items-baseline justify-between">
          <div className="text-xs text-[#64748B]" style={{ fontFamily: 'Inter, sans-serif' }}>
            Inference
          </div>
          <div className="text-sm text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.inference}
          </div>
        </div>

        <div className="flex items-baseline justify-between">
          <div className="text-xs text-[#64748B]" style={{ fontFamily: 'Inter, sans-serif' }}>
            Backend
          </div>
          <div className="text-sm text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.backend}
          </div>
        </div>

        <div className="flex items-baseline justify-between">
          <div className="text-xs text-[#64748B]" style={{ fontFamily: 'Inter, sans-serif' }}>
            Active Nodes
          </div>
          <div className="text-lg text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.activeNodes} / {stats.totalNodes}
          </div>
        </div>

        <div className="flex items-baseline justify-between">
          <div className="text-xs text-[#64748B]" style={{ fontFamily: 'Inter, sans-serif' }}>
            Frames/sec
          </div>
          <div className="text-lg text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.framesPerSec}
          </div>
        </div>
      </div>
    </div>
  );
}
