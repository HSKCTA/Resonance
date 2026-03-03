import { ArrowRight } from "lucide-react";

interface PipelineLatencyProps {
  latency: {
    dsp: number;
    ai: number;
    alert: number;
  };
}

export function PipelineLatency({ latency }: PipelineLatencyProps) {
  const total = latency.dsp + latency.ai + latency.alert;
  
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded p-4">
      <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
        PIPELINE LATENCY
      </div>
      
      <div className="flex items-center justify-center gap-2 mb-5">
        <div className="bg-[#1E293B] border border-[#334155] rounded px-3 py-2 text-center">
          <div className="text-xs text-[#64748B] mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>DSP</div>
          <div className="text-base text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {latency.dsp}ms
          </div>
        </div>
        
        <ArrowRight className="text-[#475569]" size={14} />
        
        <div className="bg-[#1E293B] border border-[#334155] rounded px-3 py-2 text-center">
          <div className="text-xs text-[#64748B] mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>AI</div>
          <div className="text-base text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {latency.ai}ms
          </div>
        </div>
        
        <ArrowRight className="text-[#475569]" size={14} />
        
        <div className="bg-[#1E293B] border border-[#334155] rounded px-3 py-2 text-center">
          <div className="text-xs text-[#64748B] mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>ALERT</div>
          <div className="text-base text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
            {latency.alert}ms
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-xs text-[#64748B] mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>TOTAL</div>
        <div className={`text-xl font-bold ${total < 100 ? "text-white" : "text-[#f59e0b]"}`} style={{ fontFamily: 'Inter, sans-serif' }}>
          {total}ms
        </div>
      </div>
    </div>
  );
}
