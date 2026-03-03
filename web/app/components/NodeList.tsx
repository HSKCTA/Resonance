import { motion } from "motion/react";

interface Node {
  id: string;
  name: string;
  status: "healthy" | "warning" | "critical";
}

interface NodeListProps {
  nodes: Node[];
  activeNode: string;
  onSelectNode: (nodeId: string) => void;
}

export function NodeList({ nodes, activeNode, onSelectNode }: NodeListProps) {
  return (
    <div className="w-56 bg-[#0F172A] border-r border-[#1E293B] flex flex-col">
      <div className="px-4 py-3 border-b border-[#1E293B]">
        <div className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wide" style={{ fontFamily: 'Inter, sans-serif' }}>
          NODES
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {nodes.map((node) => (
          <motion.button
            key={node.id}
            onClick={() => onSelectNode(node.id)}
            className={`w-full px-4 py-2.5 border-b border-[#1E293B] text-left transition-colors ${
              activeNode === node.id ? "bg-[#1E293B]" : "hover:bg-[#1E293B]/50"
            }`}
            animate={node.status === "warning" ? {
              backgroundColor: ["#0F172A", "#f59e0b15", "#0F172A"],
            } : {}}
            transition={{
              duration: 2,
              repeat: node.status === "warning" ? Infinity : 0,
              ease: "easeInOut"
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <div className={`w-1.5 h-1.5 rounded-full ${
                node.status === "healthy" ? "bg-[#10b981]" :
                node.status === "warning" ? "bg-[#f59e0b]" :
                "bg-[#ef4444]"
              }`}></div>
              <span className="text-[#E2E8F0] text-xs font-semibold" style={{ fontFamily: 'Inter, sans-serif' }}>
                {node.id}
              </span>
            </div>
            <div className="text-xs text-[#64748B] ml-3.5" style={{ fontFamily: 'Inter, sans-serif' }}>
              {node.name}
            </div>
          </motion.button>
        ))}
        
        <button className="w-full px-4 py-2.5 border-b border-[#1E293B] text-left hover:bg-[#1E293B]/50 transition-colors">
          <div className="text-[#3B82F6] text-xs font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
            + Add Node
          </div>
        </button>
      </div>
    </div>
  );
}
