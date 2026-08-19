"use client";

import React from "react";
import { useSimulationStore, AgentLog } from "@/store/useSimulationStore";
import { Cpu, Terminal, Sparkles, AlertCircle } from "lucide-react";

export const AgentConsole: React.FC = () => {
  const { agent_logs } = useSimulationStore();

  const getAgentBadge = (agentName: string) => {
    switch (agentName.toLowerCase()) {
      case "orchestrator":
        return <span className="bg-[#7F1D1D] text-[#EF4444] border border-[#DC2626]/50 text-[10px] font-mono font-bold px-2 py-0.5 rounded flex items-center gap-1"><Cpu className="w-3 h-3" /> ORCHESTRATOR (YÖNETİCİ)</span>;
      case "journalist":
        return <span className="bg-amber-950/60 text-[#D4AF37] border border-amber-600/40 text-[10px] font-mono font-bold px-2 py-0.5 rounded flex items-center gap-1"><Sparkles className="w-3 h-3" /> GAZETECİ</span>;
      case "troll":
        return <span className="bg-purple-950/60 text-purple-400 border border-purple-600/40 text-[10px] font-mono font-bold px-2 py-0.5 rounded flex items-center gap-1"><AlertCircle className="w-3 h-3" /> TROLL MOB (LİNÇ GRUBU)</span>;
      default:
        return <span className="bg-[#27272A] text-white text-[10px] font-mono px-2 py-0.5 rounded">{agentName}</span>;
    }
  };

  return (
    <div className="bg-[#18181B] rounded-xl border border-[#27272A] p-4 shadow-xl flex flex-col h-full min-h-[350px]">
      {/* Console Header */}
      <div className="flex items-center justify-between mb-3 border-b border-[#27272A] pb-2">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-[#EF4444]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Ajan Akıl Yürütme Konsolu (Çoklu Ajan Sürü Günlükleri)
          </h3>
        </div>
        <span className="text-[10px] font-mono text-[#94A3B8]">qwen-397b model analizleri</span>
      </div>

      {/* Log Feed */}
      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-xs max-h-[460px] pr-1">
        {agent_logs.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-center p-4 border border-dashed border-[#27272A] rounded-xl bg-[#121214]">
            <p className="text-xs text-[#94A3B8]">Henüz ajan günlüğü oluşmadı. Bir hamle göndererek analizi başlatın.</p>
          </div>
        ) : (
          agent_logs.map((log, idx) => (
            <div
              key={idx}
              className="bg-[#121214] p-3 rounded-lg border border-[#27272A] hover:border-[#3F3F46] transition"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  {getAgentBadge(log.agent_name)}
                  <span className="text-[11px] text-[#94A3B8] font-mono">{log.step}</span>
                </div>
                <span className="text-[9px] text-[#52525B]">
                  {new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </span>
              </div>

              <p className="text-xs text-[#FAFAFA] leading-relaxed mb-2 font-sans">
                {log.reasoning}
              </p>

              {/* Metrics Shift Badge if present */}
              {log.metrics_delta && (
                <div className="flex flex-wrap gap-2 text-[10px] pt-1 border-t border-[#27272A]/40">
                  {log.metrics_delta.crisis_level_delta !== undefined && (
                    <span className={`px-1.5 py-0.5 rounded font-mono ${log.metrics_delta.crisis_level_delta <= 0 ? "bg-emerald-950/60 text-emerald-400" : "bg-rose-950/60 text-rose-400"}`}>
                      Kriz: {log.metrics_delta.crisis_level_delta > 0 ? `+${log.metrics_delta.crisis_level_delta}` : log.metrics_delta.crisis_level_delta}
                    </span>
                  )}
                  {log.metrics_delta.brand_reputation_delta !== undefined && (
                    <span className={`px-1.5 py-0.5 rounded font-mono ${log.metrics_delta.brand_reputation_delta >= 0 ? "bg-emerald-950/60 text-emerald-400" : "bg-rose-950/60 text-rose-400"}`}>
                      İtibar: {log.metrics_delta.brand_reputation_delta > 0 ? `+${log.metrics_delta.brand_reputation_delta}` : log.metrics_delta.brand_reputation_delta}
                    </span>
                  )}
                  {log.metrics_delta.stock_price_impact_delta !== undefined && (
                    <span className={`px-1.5 py-0.5 rounded font-mono ${log.metrics_delta.stock_price_impact_delta >= 0 ? "bg-emerald-950/60 text-emerald-400" : "bg-rose-950/60 text-rose-400"}`}>
                      Hisse: {log.metrics_delta.stock_price_impact_delta > 0 ? `+${log.metrics_delta.stock_price_impact_delta}` : log.metrics_delta.stock_price_impact_delta}%
                    </span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
