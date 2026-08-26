"""
Data validation schemas and LangGraph State definitions for Dont Panic.
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# ==========================================
# 1. LangGraph TypedDict Shared State
# ==========================================

class SimulationState(TypedDict):
    scenario_id: str
    session_id: str
    company_context: Dict[str, Any]  # Brand name, industry, vulnerability details
    crisis_level: int                # 0 (Peace) to 100 (Total Collapse)
    brand_reputation: int            # 0 to 100
    stock_price_impact: float        # Percentage shift e.g. -14.2%
    turn_count: int
    user_action: str                 # Free-text press release, tweet, or tactical move
    mock_social_feed: List[Dict[str, Any]] # Streamed posts (author, handle, content, sentiment, engagement)
    agent_logs: List[Dict[str, Any]] # Internal reasoning logs of agents
    is_active: bool
    last_agent: Optional[str]        # Tracks recent node execution


# ==========================================
# 2. Pydantic Models for REST & WebSocket API
# ==========================================

class SocialPostSchema(BaseModel):
    id: str = Field(..., description="Unique ID for the post")
    author: str = Field(..., description="Display name of the poster or news outlet")
    handle: str = Field(..., description="Social handle or outlet code (e.g. @TechHater99)")
    avatar_type: str = Field("default", description="Avatar styling key or icon type")
    platform: Literal["twitter", "news", "reddit", "press"] = Field("twitter")
    content: str = Field(..., description="Post text or article snippet")
    sentiment: Literal["negative", "positive", "neutral", "outrage", "panic"] = Field("neutral")
    engagement: Dict[str, int] = Field(
        default_factory=lambda: {"likes": 0, "retweets": 0, "replies": 0},
        description="Engagement statistics"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentLogSchema(BaseModel):
    agent_name: str = Field(..., description="Name of agent (e.g. Orchestrator, Journalist, Troll)")
    step: str = Field(..., description="Action or reasoning phase")
    reasoning: str = Field(..., description="Internal rationale / thought trace")
    metrics_delta: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MetricsUpdateSchema(BaseModel):
    crisis_level: int
    brand_reputation: int
    stock_price_impact: float
    turn_count: int
    is_active: bool


class WebSocketMessage(BaseModel):
    event_type: Literal["agent_log", "social_post", "metrics_update", "turn_complete", "error", "simulation_started", "agent_progress"]
    data: Dict[str, Any]
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())



class ScenarioInitRequest(BaseModel):
    scenario_id: str = Field("data_breach_2026", description="Preset scenario ID")
    company_name: str = Field("AetherCorp", description="Target company name")
    industry: str = Field("FinTech & AI", description="Industry domain")
    vulnerability: str = Field("Unencrypted customer biometric data leak", description="Crisis backstory")


class UserActionRequest(BaseModel):
    session_id: str
    user_action: str = Field(..., min_length=1, description="Free text tactical move or press release")


# ==========================================
# 3. LLM Structured Output Parsing Schemas
# ==========================================

class OrchestratorOutput(BaseModel):
    reasoning: str = Field(..., description="Kullanıcının kriz müdahalesi hakkındaki detaylı Türkçe stratejik değerlendirme ve mantık zinciri (Chain-of-Thought)")
    crisis_level_delta: int = Field(..., description="Kriz şiddet seviyesindeki sayısal değişim (-30 ile 30 arası tam sayı)")
    brand_reputation_delta: int = Field(..., description="Marka itibar puanındaki sayısal değişim (-30 ile 30 arası tam sayı)")
    stock_price_impact_delta: float = Field(..., description="Borsa hisse fiyatındaki yüzde değişim (-15.0 ile 10.0 arası ondalık sayı)")


class JournalistOutput(BaseModel):
    outlet_name: str = Field(..., description="Medya organının adı (Örn: Bloomberg Türkiye, TeknoKriz Haber, HürMedya)")
    outlet_handle: str = Field(..., description="Medya organının sosyal medya kullanıcı adı (Örn: @TeknoKriz)")
    headline: str = Field(..., description="Türkçe yazılmış dikkat çekici son dakika haber başlığı veya özet metni")
    sentiment: Literal["negative", "positive", "neutral", "panic"] = Field(..., description="Ana akım medyanın haber tonu")
    reasoning: str = Field(..., description="Gazetecinin bu haberi bu tonda yazmasının Türkçe mantıksal gerekçesi")
    estimated_likes: int = Field(default=5000, description="Tahmini beğeni sayısı")
    estimated_retweets: int = Field(default=1500, description="Tahmini yeniden paylaşım sayısı")
    estimated_replies: int = Field(default=600, description="Tahmini yorum sayısı")


class TrollOutput(BaseModel):
    handle_name: str = Field(..., description="Sosyal medya kullanıcısının ekran adı (Örn: Anonim Yazılımcı, Kriz Savar)")
    handle_tag: str = Field(..., description="Sosyal medya kullanıcı adı (Örn: @kriz_savar)")
    post_content: str = Field(..., description="Türkçe yazılmış viralleşen, esprili, linç veya mizah içeren sosyal medya paylaşımı/tweet")
    sentiment: Literal["outrage", "negative", "neutral", "positive"] = Field(..., description="Halkın ve sosyal medyanın tepki tonu")
    reasoning: str = Field(..., description="Sosyal medya kullanıcısının bu tepkiyi vermesinin Türkçe mantıksal gerekçesi")
    estimated_likes: int = Field(default=25000, description="Tahmini beğeni sayısı")
    estimated_retweets: int = Field(default=8000, description="Tahmini yeniden paylaşım sayısı")
    estimated_replies: int = Field(default=3500, description="Tahmini yorum sayısı")

