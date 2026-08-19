"use client";

import React, { useState } from "react";
import { useSimulationStore } from "@/store/useSimulationStore";
import { Send, Zap, AlertTriangle, ShieldCheck, Loader2 } from "lucide-react";

interface CrisisTerminalProps {
  onSendAction: (actionText: string) => boolean;
}

export const CrisisTerminal: React.FC<CrisisTerminalProps> = ({ onSendAction }) => {
  const { user_action_input, setUserActionInput, is_processing, progress_status, error_message, company_name } = useSimulationStore();
  const [localError, setLocalError] = useState<string | null>(null);

  const presets = [
    {
      title: "Samimi Özür & Kredi Koruma",
      text: "Güvenlik açığından dolayı içtenlikle özür dileriz. Açık kapatıldı ve etkilenen tüm kullanıcılara 2 yıl ücretsiz kredi koruması sunuyoruz."
    },
    {
      title: "Sert Yalanlama & Karşı Dava",
      text: "Bu iddialar tamamen asılsız ve kötü niyetlidir. Sistemlerimiz güvendedir ve bu dezenformasyonu yayanlara karşı yasal işlem başlatıyoruz."
    },
    {
      title: "Üçüncü Taraf Tedarikçiyi Suçlama",
      text: "Yetkisiz erişim, izole edilmiş bir üçüncü taraf tedarikçi zincirinde gerçekleşmiştir. AetherCorp ana sistemleri etkilenmemiştir."
    },
    {
      title: "Teknik Yama Bilgilendirmesi",
      text: "Mühendislik ekibimiz güvenlik açığını tespit etmiş ve 45 dakika içinde yamayı canlıya almıştır. Sistem kayıtlarında sızıntı yoktur."
    }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!user_action_input.trim()) {
      setLocalError("Lütfen bir yanıt yazın veya hazır stratejilerden birini seçin.");
      return;
    }

    setLocalError(null);
    const success = onSendAction(user_action_input.trim());
    if (success) {
      setUserActionInput("");
    }
  };

  return (
    <div className="bg-[#18181B] rounded-xl border border-[#27272A] p-4 shadow-xl flex flex-col">
      {/* Terminal Header */}
      <div className="flex items-center justify-between mb-3 border-b border-[#27272A] pb-2">
        <div className="flex items-center space-x-2">
          <Zap className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Eylem Kontrol Merkezi (Taktik Müdahale Terminali)
          </h3>
        </div>
        <span className="text-[10px] text-[#94A3B8] font-mono">
          <span className="text-white font-bold">{company_name}</span> için resmi basın bülteni veya kriz hamlenizi oluşturun
        </span>
      </div>

      {/* Preset Buttons */}
      <div className="mb-3">
        <span className="text-[10px] uppercase font-bold text-[#94A3B8] tracking-wider block mb-1.5">
          Taktik Müdahale Şablonları:
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {presets.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setUserActionInput(preset.text);
                setLocalError(null);
              }}
              className="text-left p-2 rounded-lg bg-[#121214] border border-[#27272A] hover:border-[#D4AF37]/60 transition group text-xs"
            >
              <div className="font-semibold text-white group-hover:text-[#D4AF37] transition flex items-center justify-between">
                <span>{preset.title}</span>
                <span className="text-[9px] text-[#52525B] font-mono">Kullan →</span>
              </div>
              <p className="text-[10px] text-[#94A3B8] line-clamp-1 mt-0.5 font-sans">
                {preset.text}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
        <div className="relative">
          <textarea
            value={user_action_input}
            onChange={(e) => {
              setUserActionInput(e.target.value);
              setLocalError(null);
            }}
            placeholder="Resmi basın bülteninizi, tweet'inizi veya taktik kriz hamlenizi buraya yazın..."
            rows={3}
            disabled={is_processing}
            className="w-full bg-[#121214] border border-[#27272A] rounded-xl p-3 text-xs text-white placeholder-[#52525B] focus:outline-none focus:border-[#DC2626] transition resize-none font-sans"
          />
        </div>

        {/* Live Streaming Progress Indicator */}
        {is_processing && (
          <div className="bg-[#121214] border border-[#D4AF37]/40 rounded-xl p-3 space-y-2 animate-pulse">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-[#D4AF37]" />
                <span className="font-mono text-[#D4AF37] font-bold">
                  {progress_status?.status_message || "Yapay zeka ajanları kriz müdahalesini analiz ediyor..."}
                </span>
              </div>
              <span className="font-mono text-xs text-[#94A3B8] font-bold">
                %{progress_status?.percentage || 10}
              </span>
            </div>
            <div className="w-full bg-[#27272A] h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-gradient-to-r from-[#DC2626] via-[#D4AF37] to-[#EF4444] h-full transition-all duration-500 ease-out"
                style={{ width: `${progress_status?.percentage || 10}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Messages */}
        {(localError || error_message) && (
          <div className="bg-[#7F1D1D]/40 border border-[#DC2626] text-[#EF4444] p-2.5 rounded-lg text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{localError || error_message}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-1">
          <p className="text-[10px] text-[#94A3B8] font-mono">
            Göndermek, <span className="text-[#D4AF37]">qwen-397b</span> modeli üzerinden anlık çoklu-ajan değerlendirmesini tetikler.
          </p>

          <button
            type="submit"
            disabled={is_processing}
            className={`px-5 py-2.5 rounded-xl font-mono text-xs font-bold uppercase tracking-wider flex items-center space-x-2 transition ${
              is_processing
                ? "bg-[#27272A] text-[#94A3B8] cursor-not-allowed"
                : "bg-gradient-to-r from-[#DC2626] to-[#7F1D1D] hover:from-[#EF4444] hover:to-[#DC2626] text-white shadow-lg glow-crimson"
            }`}
          >
            {is_processing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#EF4444]" />
                <span>DEĞERLENDİRİLİYOR...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>KRİZ MÜDAHALESİNİ YAYINLA</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
