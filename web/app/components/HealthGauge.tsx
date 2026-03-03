import { motion } from "motion/react";

interface HealthGaugeProps {
  score: number;
  status: "healthy" | "warning" | "critical";
}

export function HealthGauge({ score, status }: HealthGaugeProps) {
  const color = status === "healthy" ? "#10b981" : status === "warning" ? "#f59e0b" : "#ef4444";
  const percentage = Math.min(score * 100, 100);
  
  // Calculate SVG arc path
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const dashoffset = circumference - (percentage / 100) * circumference * 0.75; // 270 degrees
  
  // Calculate needle position on the arc
  // Arc goes from -135deg to 135deg (270 degrees total)
  const angleRange = 270;
  const startAngle = -135;
  const needleAngle = startAngle + (percentage / 100) * angleRange;
  const needleRad = (needleAngle * Math.PI) / 180;
  const needleX = 100 + radius * Math.cos(needleRad);
  const needleY = 100 + radius * Math.sin(needleRad);
  
  return (
    <div className="bg-[#1a2035] border border-[#1f2937] rounded p-4 flex flex-col items-center justify-center">
      <div className="text-xs text-[#6b7280] uppercase tracking-wider mb-3">Current Health</div>
      
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full -rotate-[135deg]" viewBox="0 0 200 200">
          {/* Background arc */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#1f2937"
            strokeWidth="12"
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
          />
          {/* Foreground arc */}
          <motion.circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
            strokeDashoffset={dashoffset}
            strokeLinecap="round"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashoffset }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
          {/* Needle indicator */}
          <motion.circle
            cx={needleX}
            cy={needleY}
            r="6"
            fill={color}
            initial={{ cx: 100 - radius * Math.cos((startAngle * Math.PI) / 180), cy: 100 - radius * Math.sin((startAngle * Math.PI) / 180) }}
            animate={{ cx: needleX, cy: needleY }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div 
            className="text-3xl font-bold text-white"
            key={score}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {score.toFixed(3)}
          </motion.div>
          <div className="text-xs text-[#6b7280] mt-1">RECONSTRUCTION ERROR</div>
        </div>
      </div>
      
      <motion.div 
        className={`text-sm font-semibold mt-2 uppercase tracking-wider`}
        style={{ color }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {status}
      </motion.div>
    </div>
  );
}