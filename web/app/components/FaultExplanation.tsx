import { motion } from "motion/react";
import { AlertTriangle } from "lucide-react";
import { useState } from "react";

interface FaultExplanationProps {
  hasAnomaly: boolean;
  score: number;
  threshold: number;
  explanation?: {
    en: string;
    hi: string;
    mr: string;
  };
}

type Language = "en" | "hi" | "mr";

export function FaultExplanation({ hasAnomaly, score, threshold, explanation }: FaultExplanationProps) {
  const [language, setLanguage] = useState<Language>("en");
  
  const languages: Array<{ code: Language; label: string }> = [
    { code: "en", label: "EN" },
    { code: "hi", label: "HI" },
    { code: "mr", label: "MR" },
  ];
  
  return (
    <motion.div 
      className={`bg-[#0F172A] border rounded p-4 ${
        hasAnomaly ? "border-[#f59e0b]" : "border-[#1E293B]"
      }`}
      animate={{
        borderColor: hasAnomaly ? "#f59e0b" : "#1E293B",
      }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide" style={{ fontFamily: 'Inter, sans-serif' }}>
          ALERT STATUS
        </div>
        
        {hasAnomaly && (
          <div className="flex gap-1">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`px-2 py-0.5 text-xs rounded transition-colors ${
                  language === lang.code
                    ? "bg-[#3B82F6] text-white"
                    : "bg-[#1E293B] text-[#64748B] hover:text-[#94A3B8]"
                }`}
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                {lang.label}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {hasAnomaly && explanation ? (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="text-[#f59e0b]" size={16} />
            <div className="text-[#f59e0b] font-semibold text-xs uppercase tracking-wide" style={{ fontFamily: 'Inter, sans-serif' }}>
              ANOMALY DETECTED
            </div>
          </div>
          
          <div className="mb-3 text-xs" style={{ fontFamily: 'Inter, sans-serif' }}>
            <div className="text-[#64748B]">
              Score: <span className="text-white font-semibold">{score.toFixed(3)}</span>
              {" — "}
              Threshold: <span className="text-white font-semibold">{threshold.toFixed(3)}</span>
            </div>
          </div>
          
          <div className="bg-[#1E293B] rounded px-3 py-2">
            <div className="text-xs text-[#94A3B8] leading-relaxed" style={{ fontFamily: 'Inter, sans-serif' }}>
              {explanation[language]}
            </div>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="py-2"
        >
          <div className="text-[#10b981] text-xs font-semibold flex items-center gap-2" style={{ fontFamily: 'Inter, sans-serif' }}>
            <div className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></div>
            System Normal
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
