"use client";

import React, { useState } from "react";
import { useSimulationStore, SocialPost } from "@/store/useSimulationStore";
import { MessageSquare, Heart, Repeat, Newspaper, Share2, Flame, ShieldCheck } from "lucide-react";

export const SocialFeed: React.FC = () => {
  const { mock_social_feed } = useSimulationStore();
  const [activeFilter, setActiveFilter] = useState<"all" | "news" | "twitter">("all");

  const filteredPosts = mock_social_feed.filter((post) => {
    if (activeFilter === "news") return post.platform === "news";
    if (activeFilter === "twitter") return post.platform === "twitter";
    return true;
  });

  const getSentimentBadge = (sentiment: SocialPost["sentiment"]) => {
    switch (sentiment) {
      case "outrage":
      case "panic":
        return <span className="bg-[#7F1D1D] text-[#EF4444] border border-[#DC2626]/50 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded flex items-center gap-1"><Flame className="w-3 h-3" /> TEBKİ / LİNÇ</span>;
      case "negative":
        return <span className="bg-amber-950/60 text-amber-400 border border-amber-600/40 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded">OLUMSUZ</span>;
      case "positive":
        return <span className="bg-emerald-950/60 text-emerald-400 border border-emerald-600/40 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> OLUMLU</span>;
      default:
        return <span className="bg-[#27272A] text-[#94A3B8] border border-[#3F3F46] text-[10px] font-extrabold uppercase px-2 py-0.5 rounded">NÖTR</span>;
    }
  };

  return (
    <div className="bg-[#18181B] rounded-xl border border-[#27272A] p-4 shadow-xl flex flex-col h-full min-h-[400px]">
      {/* Header & Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4 border-b border-[#27272A] pb-3">
        <div className="flex items-center space-x-2">
          <Share2 className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Simüle İnternet Ekosistemi (Sosyal Medya & Basın Akışı)
          </h3>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1 bg-[#121214] p-1 rounded-lg border border-[#27272A]">
          <button
            onClick={() => setActiveFilter("all")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition ${
              activeFilter === "all" ? "bg-[#27272A] text-white" : "text-[#94A3B8] hover:text-white"
            }`}
          >
            Tüm Akış ({mock_social_feed.length})
          </button>
          <button
            onClick={() => setActiveFilter("news")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition flex items-center gap-1 ${
              activeFilter === "news" ? "bg-[#27272A] text-white" : "text-[#94A3B8] hover:text-white"
            }`}
          >
            <Newspaper className="w-3 h-3" /> Basın Bültenleri
          </button>
          <button
            onClick={() => setActiveFilter("twitter")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition flex items-center gap-1 ${
              activeFilter === "twitter" ? "bg-[#27272A] text-white" : "text-[#94A3B8] hover:text-white"
            }`}
          >
            <Share2 className="w-3 h-3" /> Sosyal Tepki
          </button>
        </div>
      </div>

      {/* Posts Stream */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[520px]">
        {filteredPosts.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-center p-6 border border-dashed border-[#27272A] rounded-xl bg-[#121214]">
            <Share2 className="w-8 h-8 text-[#27272A] mb-2 animate-bounce" />
            <p className="text-xs font-mono text-[#94A3B8]">Kriz hamlesi bekleniyor...</p>
            <p className="text-[10px] text-[#52525B] mt-1">
              Aşağıdaki terminalden tepkinizi göndererek gazetecilerin ve internet trollerinin canlı yanıtlarını tetikleyin.
            </p>
          </div>
        ) : (
          filteredPosts.map((post) => (
            <div
              key={post.id}
              className={`p-3.5 rounded-xl border transition-all ${
                post.sentiment === "outrage" || post.sentiment === "panic"
                  ? "bg-[#1C1818] border-[#7F1D1D]/60 hover:border-[#DC2626]"
                  : "bg-[#121214] border-[#27272A] hover:border-[#3F3F46]"
              }`}
            >
              {/* Card Top */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-7 h-7 rounded-full bg-[#27272A] flex items-center justify-center text-white font-bold text-xs font-mono">
                    {post.platform === "news" ? <Newspaper className="w-3.5 h-3.5 text-[#D4AF37]" /> : <Share2 className="w-3.5 h-3.5 text-sky-400" />}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                      {post.author}
                      <span className="text-[11px] font-normal text-[#94A3B8] font-mono">{post.handle}</span>
                    </h4>
                  </div>
                </div>
                {getSentimentBadge(post.sentiment)}
              </div>

              {/* Card Content */}
              <p className="text-xs text-[#FAFAFA] leading-relaxed mb-3 font-sans">
                {post.content}
              </p>

              {/* Card Footer Engagement */}
              <div className="flex items-center justify-between text-[10px] text-[#94A3B8] font-mono border-t border-[#27272A]/60 pt-2">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center space-x-1 hover:text-rose-400 transition">
                    <Heart className="w-3 h-3" />
                    <span>{post.engagement?.likes?.toLocaleString() || 0}</span>
                  </span>
                  <span className="flex items-center space-x-1 hover:text-emerald-400 transition">
                    <Repeat className="w-3 h-3" />
                    <span>{post.engagement?.retweets?.toLocaleString() || 0}</span>
                  </span>
                  <span className="flex items-center space-x-1 hover:text-sky-400 transition">
                    <MessageSquare className="w-3 h-3" />
                    <span>{post.engagement?.replies?.toLocaleString() || 0}</span>
                  </span>
                </div>
                <span className="text-[9px] text-[#52525B]">
                  {new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
