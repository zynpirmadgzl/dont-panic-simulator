"use client";

import React, { useState } from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import { X, Layers, AlertOctagon, Check } from "lucide-react";

interface ScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ScenarioModal: React.FC<ScenarioModalProps> = ({ isOpen, onClose }) => {
  const { setSession, scenario_id } = useSimulationStore();
  const [selectedScenario, setSelectedScenario] = useState(scenario_id);

  if (!isOpen) return null;

  const presets = [
    {
      id: "data_breach_2026",
      title: "Şifrelenmemiş Biyometrik Veri Sızıntısı",
      company_name: "AetherCorp",
      industry: "FinTech & Yapay Zeka",
      vulnerability: "4 milyon şifrelenmemiş yüz tanıma verisi karanlık ağda sızdırıldı.",
      initial_crisis: 55
    },
    {
      id: "ai_hallucination_scandal",
      title: "Otonom Tıbbi Yapay Zeka Hatası",
      company_name: "MediPulse AI",
      industry: "Sağlık Teknolojileri",
      vulnerability: "Teşhis yapay zekası klinik deneme aşamasında çelişkili dozaj önerileri verdi.",
      initial_crisis: 70
    },
    {
      id: "ceo_deepfake_leak",
      title: "CEO Deepfake İhbar Skandalı",
      company_name: "Vanguard Dynamics",
      industry: "Savunma Sanayi",
      vulnerability: "CEO'nun içsel bilgi ticareti (insider trading) yaptığını iddia eden sentetik ses kaydı yayıldı.",
      initial_crisis: 65
    }
  ];

  const handleSelectScenario = (preset: typeof presets[0]) => {
    setSelectedScenario(preset.id);
    const newSessionId = `session_${Date.now()}`;
    setSession(newSessionId, preset.company_name, preset.industry, preset.vulnerability, preset.id);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#18181B] border border-[#27272A] rounded-2xl w-full max-w-xl p-6 shadow-2xl relative glow-crimson">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#94A3B8] hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 mb-4 border-b border-[#27272A] pb-3">
          <Layers className="w-5 h-5 text-[#D4AF37]" />
          <h2 className="text-base font-extrabold uppercase tracking-wider text-white font-mono">
            Kriz Simülasyon Senaryosu Seçin
          </h2>
        </div>

        <div className="space-y-3 mb-6">
          {presets.map((preset) => {
            const isSelected = selectedScenario === preset.id;
            return (
              <div
                key={preset.id}
                onClick={() => handleSelectScenario(preset)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-[#201515] border-[#DC2626]"
                    : "bg-[#121214] border-[#27272A] hover:border-[#3F3F46]"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <AlertOctagon className={`w-4 h-4 ${isSelected ? "text-[#EF4444]" : "text-[#D4AF37]"}`} />
                    <h3 className="text-sm font-bold text-white">{preset.title}</h3>
                  </div>
                  {isSelected && <Check className="w-4 h-4 text-[#EF4444]" />}
                </div>

                <div className="flex items-center space-x-3 text-xs font-mono text-[#D4AF37] mb-2">
                  <span>{preset.company_name}</span>
                  <span>•</span>
                  <span>{preset.industry}</span>
                  <span>•</span>
                  <span className="text-rose-400 font-bold">Severity {preset.initial_crisis}/100</span>
                </div>

                <p className="text-xs text-[#94A3B8]">
                  {preset.vulnerability}
                </p>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-end space-x-3 border-t border-[#27272A] pt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#94A3B8] hover:text-white bg-[#121214] border border-[#27272A] transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
