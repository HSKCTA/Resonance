import { motion } from "motion/react";

interface Harmonic {
  label: string;
  frequency: number;
  level: number; // 0-1
  status: "nominal" | "elevated" | "critical";
}

interface HarmonicAnalysisProps {
  harmonics: Harmonic[];
}

export function HarmonicAnalysis({ harmonics }: HarmonicAnalysisProps) {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded p-4">
      <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
        HARMONIC ANALYSIS
      </div>
      
      <div className="space-y-4">
        {harmonics.map((harmonic, index) => {
          const color = harmonic.status === "nominal" ? "#64748B" : 
                       harmonic.status === "elevated" ? "#f59e0b" : "#ef4444";
          
          return (
            <div key={index}>
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs text-[#94A3B8] font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
                  {harmonic.label}
                </div>
                <div className="text-sm text-white font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
                  {harmonic.frequency} Hz
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex-1 h-1.5 bg-[#1E293B] rounded-sm overflow-hidden">
                  <motion.div 
                    className="h-full"
                    style={{ backgroundColor: color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${harmonic.level * 100}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
                
                <div className="text-xs uppercase tracking-wide w-16 text-right font-medium" style={{ color, fontFamily: 'Inter, sans-serif' }}>
                  {harmonic.status}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
