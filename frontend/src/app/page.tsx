"use client";

import React, { useState } from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { HeaderNav } from "@/components/HeaderNav";
import { TelemetryStrip } from "@/components/TelemetryStrip";
import { TelemetryChart } from "@/components/TelemetryChart";
import { SocialFeed } from "@/components/SocialFeed";
import { AgentConsole } from "@/components/AgentConsole";
import { CrisisTerminal } from "@/components/CrisisTerminal";
import { ScenarioModal } from "@/components/ScenarioModal";

export default function CrisisDashboard() {
  const { session_id, company_name, industry, vulnerability } = useSimulationStore();
  const { sendAction } = useWebSocket(session_id);
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0B0B0B] text-[#FAFAFA] flex flex-col font-sans selection:bg-[#DC2626] selection:text-white">
      {/* 1. Header Navigation */}
      <HeaderNav onOpenScenarioModal={() => setIsScenarioModalOpen(true)} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* Scenario Overview Banner */}
        <div className="bg-gradient-to-r from-[#18181B] via-[#1C1818] to-[#18181B] border border-[#27272A] p-4 rounded-xl shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-[#EF4444] animate-ping" />
              <h2 className="text-xs font-mono font-bold uppercase tracking-widest text-[#D4AF37]">
                AKTİF KRİZ SENARYOSU
              </h2>
            </div>
            <h3 className="text-sm font-black text-white mt-0.5">
              {company_name} ({industry}) — Kriz Arka Planı
            </h3>
            <p className="text-xs text-[#94A3B8] mt-1 font-sans">
              {vulnerability}
            </p>
          </div>

          <div className="bg-[#121214] px-3 py-2 rounded-lg border border-[#27272A] text-[11px] font-mono text-[#94A3B8] shrink-0">
            Yapay Zeka Motoru: <span className="text-white font-bold">qwen-397b Multi-Agent</span>
          </div>
        </div>

        {/* 2. Top Telemetry Meters */}
        <TelemetryStrip />

        {/* 3. Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Simulated Ecosystem Social & News Feed (5 Cols) */}
          <div className="lg:col-span-5 h-full">
            <SocialFeed />
          </div>

          {/* Right Column: Telemetry History Chart + Agent Console (7 Cols) */}
          <div className="lg:col-span-7 flex flex-col space-y-6">
            <TelemetryChart />
            <AgentConsole />
          </div>
        </div>

        {/* 4. Action Control Center (Terminal) */}
        <CrisisTerminal onSendAction={sendAction} />
      </main>

      {/* Footer */}
      <footer className="border-t border-[#27272A] bg-[#0B0B0B] py-4 px-6 text-center text-xs text-[#52525B] font-mono">
        PROJECT DONT PANIC — Next-Gen AI-Native Crisis Communication Simulator © 2026
      </footer>

      {/* Scenario Selection Modal */}
      <ScenarioModal
        isOpen={isScenarioModalOpen}
        onClose={() => setIsScenarioModalOpen(false)}
      />
    </div>
  );
}
