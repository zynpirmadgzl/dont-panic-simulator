"use client";

import React from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import { ShieldAlert, Radio, RefreshCw, Layers } from "lucide-react";

interface HeaderNavProps {
  onOpenScenarioModal: () => void;
}

export const HeaderNav: React.FC<HeaderNavProps> = ({ onOpenScenarioModal }) => {
  const {
    company_name,
    turn_count,
    ws_connected,
    is_processing,
    resetSession
  } = useSimulationStore();

  return (
    <header className="w-full bg-[#121214] border-b border-[#27272A] px-4 py-3 sm:px-6 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40 shadow-xl">
      {/* Brand & Project Identity */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#DC2626] to-[#7F1D1D] flex items-center justify-center shadow-lg glow-crimson">
          <ShieldAlert className="w-5 h-5 text-white animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-black tracking-wider uppercase text-white font-mono">
              DONT PANIC
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest bg-[#7F1D1D] text-[#EF4444] rounded border border-[#DC2626]/40">
              AI-Tabanlı Kriz Simülatörü
            </span>
          </div>
          <p className="text-xs text-[#94A3B8]">
            Hedef Şirket: <span className="text-white font-semibold">{company_name}</span> Simülasyon Sistemi
          </p>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="flex items-center space-x-3 text-xs">
        {/* Live WebSocket Connection Pill */}
        <div className="flex items-center space-x-2 bg-[#18181B] px-3 py-1.5 rounded-full border border-[#27272A]">
          <Radio className={`w-3.5 h-3.5 ${ws_connected ? "text-emerald-400 animate-pulse" : "text-rose-500"}`} />
          <span className="font-mono font-medium text-[#FAFAFA]">
            {ws_connected ? "MOTOR CANLI" : "BAĞLANTI KESİLDİ"}
          </span>
        </div>

        {/* Turn Counter Badge */}
        <div className="bg-[#18181B] px-3 py-1.5 rounded-full border border-[#27272A] flex items-center space-x-1.5">
          <span className="text-[#94A3B8] font-mono">TUR:</span>
          <span className="font-mono font-bold text-[#D4AF37]">{turn_count}</span>
        </div>

        {/* Processing Indicator */}
        {is_processing && (
          <div className="flex items-center space-x-2 bg-[#7F1D1D]/30 border border-[#DC2626] px-3 py-1.5 rounded-full animate-pulse">
            <div className="w-2 h-2 rounded-full bg-[#EF4444] animate-ping" />
            <span className="text-[#EF4444] font-mono font-bold text-xs">
              QWEN-397B DEĞERLENDİRİYOR...
            </span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onOpenScenarioModal}
          className="flex items-center space-x-1.5 bg-[#18181B] hover:bg-[#202023] text-xs font-semibold text-white px-3 py-2 rounded-md border border-[#27272A] transition"
        >
          <Layers className="w-3.5 h-3.5 text-[#D4AF37]" />
          <span>Senaryo Değiştir</span>
        </button>

        <button
          onClick={resetSession}
          title="Kriz Durumunu Sıfırla"
          className="flex items-center space-x-1 bg-[#18181B] hover:bg-[#202023] text-xs text-[#94A3B8] hover:text-white p-2 rounded-md border border-[#27272A] transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
