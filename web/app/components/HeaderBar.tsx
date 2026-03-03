interface HeaderBarProps {
  connected: boolean;
  rms?: number;
}

export function HeaderBar({ connected, rms }: HeaderBarProps) {
  return (
    <div className="h-12 bg-[#0F172A] border-b border-[#1E293B] flex items-center justify-between px-6">
      <div className="text-[#3B82F6] font-semibold tracking-tight" style={{ fontFamily: 'Inter, sans-serif', fontSize: '15px' }}>
        RESONANCE
      </div>

      <div className="text-[#E2E8F0] text-sm font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
        Compressor Bearing — Node 01
      </div>

      <div className="flex items-center gap-3">
        {rms !== undefined && (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#1E293B] border border-[#1E293B]">
            <span className="text-xs text-[#64748B] font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
              RMS
            </span>
            <span className="text-xs text-[#E2E8F0] font-semibold font-mono">
              {rms.toFixed(5)}
            </span>
          </div>
        )}

        <div className={`flex items-center gap-2 px-2.5 py-1 rounded bg-[#1E293B] border ${connected ? 'border-[#10b981]/20' : 'border-[#ef4444]/20'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`}></div>
          <span className="text-xs text-[#94A3B8] font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
            SAFETY GATE
          </span>
        </div>

        <div className={`flex items-center gap-2 px-2.5 py-1 rounded bg-[#1E293B] border ${connected ? 'border-[#10b981]/20' : 'border-[#ef4444]/20'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`}></div>
          <span className="text-xs text-[#94A3B8] font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
            {connected ? 'AI ONLINE' : 'AI OFFLINE'}
          </span>
        </div>
      </div>
    </div>
  );
}
