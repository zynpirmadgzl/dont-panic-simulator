"use client";

import React from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import { LineChart as LineChartIcon } from "lucide-react";

export const TelemetryChart: React.FC = () => {
  const { telemetry_history } = useSimulationStore();

  return (
    <div className="bg-[#18181B] rounded-xl border border-[#27272A] p-4 shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between mb-3 border-b border-[#27272A] pb-2">
        <div className="flex items-center space-x-2">
          <LineChartIcon className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Canlı Telemetri Analitiği (Tur Geçmişi)
          </h3>
        </div>
        <div className="flex items-center space-x-4 text-[10px] font-mono">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
            <span className="text-[#94A3B8]">Kriz Şiddeti</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#D4AF37]" />
            <span className="text-[#94A3B8]">İtibar Puanı</span>
          </span>
        </div>
      </div>

      <div className="w-full h-48 sm:h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={telemetry_history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCrisis" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorReputation" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#D4AF37" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} />
            <XAxis
              dataKey="turn"
              stroke="#94A3B8"
              tickLine={false}
              tickFormatter={(t) => `T${t}`}
              style={{ fontSize: "10px", fontFamily: "monospace" }}
            />
            <YAxis
              domain={[0, 100]}
              stroke="#94A3B8"
              tickLine={false}
              style={{ fontSize: "10px", fontFamily: "monospace" }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#121214",
                borderColor: "#27272A",
                borderRadius: "8px",
                fontSize: "11px",
                color: "#FAFAFA"
              }}
            />

            <Area
              type="monotone"
              dataKey="crisis_level"
              name="Crisis Severity"
              stroke="#EF4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorCrisis)"
            />

            <Area
              type="monotone"
              dataKey="brand_reputation"
              name="Reputation Score"
              stroke="#D4AF37"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorReputation)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
