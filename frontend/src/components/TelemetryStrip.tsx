"use client";

import React from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import { AlertTriangle, Award, TrendingDown, TrendingUp, Activity } from "lucide-react";

export const TelemetryStrip: React.FC = () => {
  const { crisis_level, brand_reputation, stock_price_impact, turn_count } = useSimulationStore();

  // Crisis Severity styling
  const getCrisisBadge = (level: number) => {
    if (level >= 75) return { label: "KRİTİK ÇÖKÜŞ", bg: "bg-[#7F1D1D]", text: "text-[#EF4444]", border: "border-[#DC2626]" };
    if (level >= 50) return { label: "YÜKSEK ALARM", bg: "bg-amber-950/60", text: "text-amber-400", border: "border-amber-600/50" };
    if (level >= 25) return { label: "YÜKSEK HASSASİYET", bg: "bg-yellow-950/40", text: "text-yellow-400", border: "border-yellow-600/30" };
    return { label: "DURUM STABİL / BARIŞ", bg: "bg-emerald-950/40", text: "text-emerald-400", border: "border-emerald-600/30" };
  };

  const crisisBadge = getCrisisBadge(crisis_level);
  const isStockNegative = stock_price_impact < 0;

  return (
    <section className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* 1. Crisis Severity Meter Card */}
      <div className={`bg-[#18181B] rounded-xl p-4 border ${crisis_level >= 65 ? "border-crimson-pulse bg-gradient-to-br from-[#18181B] to-[#7F1D1D]/20" : "border-[#27272A]"} shadow-lg flex flex-col justify-between relative overflow-hidden`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`p-2 rounded-lg ${crisisBadge.bg} ${crisisBadge.text}`}>
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-xs uppercase font-bold tracking-wider text-[#94A3B8]">Kriz Şiddeti Göstergesi</h2>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase ${crisisBadge.bg} ${crisisBadge.text} ${crisisBadge.border}`}>
                {crisisBadge.label}
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black font-mono text-white">{crisis_level}</span>
            <span className="text-xs text-[#94A3B8]">/100</span>
          </div>
        </div>

        {/* Dynamic Severity Progress Bar */}
        <div className="w-full bg-[#121214] h-2.5 rounded-full overflow-hidden border border-[#27272A] mt-2">
          <div
            className={`h-full transition-all duration-700 ease-out ${
              crisis_level >= 75
                ? "bg-gradient-to-r from-[#DC2626] to-[#EF4444] glow-crimson"
                : crisis_level >= 45
                ? "bg-gradient-to-r from-amber-500 to-amber-400"
                : "bg-gradient-to-r from-emerald-500 to-emerald-400"
            }`}
            style={{ width: `${Math.min(100, Math.max(0, crisis_level))}%` }}
          />
        </div>
      </div>

      {/* 2. Brand Reputation Score Card */}
      <div className="bg-[#18181B] rounded-xl p-4 border border-[#27272A] shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-lg bg-amber-950/40 text-[#D4AF37]">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-xs uppercase font-bold tracking-wider text-[#94A3B8]">Marka İtibar Endeksi</h2>
              <p className="text-[10px] text-[#94A3B8]">Halk Güven & Duygu Derecelendirmesi</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black font-mono text-[#D4AF37]">{brand_reputation}</span>
            <span className="text-xs text-[#94A3B8]">/100</span>
          </div>
        </div>

        {/* Reputation Progress Bar */}
        <div className="w-full bg-[#121214] h-2.5 rounded-full overflow-hidden border border-[#27272A] mt-2">
          <div
            className="h-full bg-gradient-to-r from-[#D4AF37] to-amber-300 transition-all duration-700 ease-out glow-gold"
            style={{ width: `${Math.min(100, Math.max(0, brand_reputation))}%` }}
          />
        </div>
      </div>

      {/* 3. Stock Market Impact Shift Card */}
      <div className="bg-[#18181B] rounded-xl p-4 border border-[#27272A] shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`p-2 rounded-lg ${isStockNegative ? "bg-rose-950/50 text-rose-400" : "bg-emerald-950/50 text-emerald-400"}`}>
              {isStockNegative ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
            </div>
            <div>
              <h2 className="text-xs uppercase font-bold tracking-wider text-[#94A3B8]">Borsa Hisse Etkisi</h2>
              <p className="text-[10px] text-[#94A3B8]">Piyasa Değeri Değişimi</p>
            </div>
          </div>
          <div className="text-right">
            <span className={`text-2xl font-black font-mono ${isStockNegative ? "text-rose-400" : "text-emerald-400"}`}>
              {stock_price_impact > 0 ? `+${stock_price_impact}` : stock_price_impact}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-[#94A3B8] border-t border-[#27272A] pt-2 mt-1">
          <span className="flex items-center space-x-1">
            <Activity className="w-3 h-3 text-[#D4AF37]" />
            <span>Tur {turn_count} Gelişimi</span>
          </span>
          <span className="font-mono text-[10px] uppercase text-white font-bold">
            {isStockNegative ? "Düşüş Baskısı (Bearish)" : "Yükseliş Eğilimi (Bullish)"}
          </span>
        </div>
      </div>
    </section>
  );
};
