interface SystemStatsProps {
  stats: {
    sampleRate: string;
    fftSize: string;
    overlap: string;
    edgeDevice: string;
  };
}

export function SystemStats({ stats }: SystemStatsProps) {
  return (
    <div className="w-56 bg-[#0F172A] border-l border-[#1E293B] flex flex-col">
      <div className="px-4 py-3 border-b border-[#1E293B]">
        <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide" style={{ fontFamily: 'Inter, sans-serif' }}>
          SYSTEM
        </div>
      </div>
      
      <div className="flex-1 p-4 space-y-5">
        <div>
          <div className="text-xs text-[#64748B] mb-1.5" style={{ fontFamily: 'Inter, sans-serif' }}>
            Sample Rate
          </div>
          <div className="text-lg text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.sampleRate}
          </div>
        </div>
        
        <div>
          <div className="text-xs text-[#64748B] mb-1.5" style={{ fontFamily: 'Inter, sans-serif' }}>
            FFT Size
          </div>
          <div className="text-lg text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.fftSize}
          </div>
        </div>
        
        <div>
          <div className="text-xs text-[#64748B] mb-1.5" style={{ fontFamily: 'Inter, sans-serif' }}>
            Overlap
          </div>
          <div className="text-lg text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.overlap}
          </div>
        </div>
        
        <div className="pt-4 border-t border-[#1E293B]">
          <div className="text-xs text-[#64748B] mb-1.5" style={{ fontFamily: 'Inter, sans-serif' }}>
            Edge Device
          </div>
          <div className="text-sm text-[#E2E8F0] font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {stats.edgeDevice}
          </div>
          <div className="text-xs text-[#64748B] mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>
            Vitis AI
          </div>
        </div>
      </div>
    </div>
  );
}
