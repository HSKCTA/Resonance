import { motion } from "motion/react";

interface HealthScoreProps {
  score: number;
  status: "healthy" | "warning" | "critical";
}

export function HealthScore({ score, status }: HealthScoreProps) {
  const color = status === "healthy" ? "#10b981" : status === "warning" ? "#f59e0b" : "#ef4444";
  const percentage = Math.min((score / 1.0) * 100, 100);
  
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded p-4">
      <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide mb-4">CURRENT HEALTH</div>
      
      <div className="mb-3">
        <motion.div 
          className="text-[32px] font-bold text-white leading-none"
          key={score}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          {score.toFixed(3)}
        </motion.div>
        <div className="text-xs text-[#64748B] mt-1.5" style={{ fontFamily: 'Inter, sans-serif' }}>
          Reconstruction Error
        </div>
      </div>
      
      <div className="mb-3">
        <div className="h-1.5 bg-[#1E293B] rounded-sm overflow-hidden">
          <motion.div 
            className="h-full"
            style={{ backgroundColor: color }}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full`} style={{ backgroundColor: color }}></div>
        <motion.div 
          className={`text-xs font-semibold uppercase tracking-wide`}
          style={{ color, fontFamily: 'Inter, sans-serif' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {status}
        </motion.div>
      </div>
    </div>
  );
}
