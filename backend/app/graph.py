"""
LangGraph Multi-Agent Engine for Dont Panic.
Defines Orchestrator, Journalist, and Troll nodes operating on SimulationState using live qwen-397b LLM calls
via PydanticOutputParser for universal provider compatibility.
"""
import uuid
import os
import json
from typing import Dict, Any, List
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.schemas import (
    SimulationState,
    OrchestratorOutput,
    JournalistOutput,
    TrollOutput
)
from app.llm import get_llm

# Initialize Output Parsers
orchestrator_parser = PydanticOutputParser(pydantic_object=OrchestratorOutput)
journalist_parser = PydanticOutputParser(pydantic_object=JournalistOutput)
troll_parser = PydanticOutputParser(pydantic_object=TrollOutput)


# ==========================================
# Agent Node Implementations (qwen-397b)
# ==========================================

async def orchestrator_node(state: SimulationState) -> Dict[str, Any]:
    """
    Orchestrator Agent Node:
    - Calls qwen-397b via PydanticOutputParser to evaluate user action.
    - Evaluates crisis_level_delta, brand_reputation_delta, stock_price_impact_delta.
    """
    llm = get_llm(temperature=0.3)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen 'Dont Panic' AI kurumsal kriz simülasyon platformunun Lider Kriz Strateji Ajanısın (Orchestrator).
Görevin, kullanıcının kriz anında yayınladığı basın bültenini, açıklamayı veya stratejik hamleyi nesnel olarak değerlendirmektir.

ZORUNLU DİL VE FORMAT KURALI:
1. `reasoning` alanı ve tüm değerlendirme açıklamaları KESİNLİKLE %100 TÜRKÇE OLMALIDIR. İngilizce kelime veya cümle KULLANMA.
2. `crisis_level_delta`: Kriz şiddeti değişimi (-30 ile +30 arası tam sayı). Başına '+' işareti KOYMA (örn: +8 yerine 8 yaz).
3. `brand_reputation_delta`: Marka itibar puanı değişimi (-30 ile +30 arası tam sayı). Başına '+' işareti KOYMA.
4. `stock_price_impact_delta`: Borsa hisse fiyatı değişimi (-15.0 ile 10.0 arası float). Başına '+' işareti KOYMA.

Hedef Şirket Bilgileri:
- Şirket Adı: {company_name}
- Sektör: {industry}
- Kriz Zafiyeti / Arka Plan: {vulnerability}

Mevcut Metrikler:
- Kriz Şiddet Seviyesi: {crisis_level}/100
- Marka İtibar Puanı: {brand_reputation}/100
- Borsa Etkisi: %{stock_price_impact}
- Tur Sayısı: {turn_count}

Kullanıcının hamlesini dikkatle analiz et. Samimiyetsiz, yetersiz veya kaçamak açıklamalar kriz şiddetini artırır; şeffaf, yapıcı ve somut adımlar kriz şiddetini düşürür.

Cevabını ZORUNLU olarak aşağıdaki JSON formatında ver:
{format_instructions}"""),
        ("user", "Kullanıcının Kriz Hamlesi / Açıklaması: {user_action}")
    ]).partial(format_instructions=orchestrator_parser.get_format_instructions())

    company_ctx = state.get("company_context", {})
    chain = prompt | llm | orchestrator_parser

    res: OrchestratorOutput = await chain.ainvoke({
        "company_name": company_ctx.get("company_name", "AetherCorp"),
        "industry": company_ctx.get("industry", "Technology"),
        "vulnerability": company_ctx.get("vulnerability", "Unspecified vulnerability"),
        "crisis_level": state.get("crisis_level", 50),
        "brand_reputation": state.get("brand_reputation", 50),
        "stock_price_impact": state.get("stock_price_impact", 0.0),
        "turn_count": state.get("turn_count", 0),
        "user_action": state.get("user_action", "No response issued.")
    })

    current_crisis = state.get("crisis_level", 50)
    current_rep = state.get("brand_reputation", 50)
    current_stock = state.get("stock_price_impact", 0.0)

    new_crisis = max(0, min(100, current_crisis + res.crisis_level_delta))
    new_rep = max(0, min(100, current_rep + res.brand_reputation_delta))
    new_stock = round(current_stock + res.stock_price_impact_delta, 2)
    turn_count = state.get("turn_count", 0) + 1

    orchestrator_log = {
        "agent_name": "Orchestrator",
        "step": f"Tur {turn_count} Stratejik Değerlendirme (qwen-397b)",
        "reasoning": res.reasoning,
        "metrics_delta": {
            "crisis_level_delta": res.crisis_level_delta,
            "brand_reputation_delta": res.brand_reputation_delta,
            "stock_price_impact_delta": res.stock_price_impact_delta
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    updated_agent_logs = list(state.get("agent_logs", [])) + [orchestrator_log]

    return {
        "crisis_level": new_crisis,
        "brand_reputation": new_rep,
        "stock_price_impact": new_stock,
        "turn_count": turn_count,
        "agent_logs": updated_agent_logs,
        "last_agent": "Orchestrator"
    }


async def journalist_node(state: SimulationState) -> Dict[str, Any]:
    """
    Journalist Agent Node:
    - Calls qwen-397b via PydanticOutputParser to generate media coverage.
    """
    llm = get_llm(temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen 'Dont Panic' kriz simülasyonundaki Medya ve Gazeteci Ajanısın (Journalist).
Prestijli ekonomi ve teknoloji basın organlarını (örn: Bloomberg Türkiye, TeknoKriz Haber, HürMedya, FinansGündem) temsil ediyorsun.

ZORUNLU DİL KURALI:
`headline` (son dakika haber başlığı) ve `reasoning` (gerekçe) alanları KESİNLİKLE %100 TÜRKÇE OLMALIDIR.

Şirket Bilgileri:
- Şirket Adı: {company_name}
- Mevcut Kriz Şiddeti: {crisis_level}/100
- Kullanıcının Son Basın Açıklaması: '{user_action}'

Kullanıcının açıklamasına yanıt olarak gazeteci gözüyle dikkat çekici, gerçekçi bir Türkçe son dakika kriz haberi başlığı üret.

Cevabını ZORUNLU olarak aşağıdaki JSON formatında ver:
{format_instructions}"""),
        ("user", "Son dakika kriz haberini hazırla.")
    ]).partial(format_instructions=journalist_parser.get_format_instructions())

    company_ctx = state.get("company_context", {})
    chain = prompt | llm | journalist_parser

    res: JournalistOutput = await chain.ainvoke({
        "company_name": company_ctx.get("company_name", "AetherCorp"),
        "crisis_level": state.get("crisis_level", 50),
        "user_action": state.get("user_action", "Açıklama yapılmadı.")
    })

    news_post = {
        "id": str(uuid.uuid4()),
        "author": res.outlet_name,
        "handle": res.outlet_handle,
        "avatar_type": "news_badge",
        "platform": "news",
        "content": res.headline,
        "sentiment": res.sentiment,
        "engagement": {
            "likes": res.estimated_likes,
            "retweets": res.estimated_retweets,
            "replies": res.estimated_replies
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    journalist_log = {
        "agent_name": "Journalist",
        "step": "Medya Çerçeveleme Analizi (qwen-397b)",
        "reasoning": res.reasoning,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    feed = list(state.get("mock_social_feed", [])) + [news_post]
    logs = list(state.get("agent_logs", [])) + [journalist_log]

    return {
        "mock_social_feed": feed,
        "agent_logs": logs,
        "last_agent": "Journalist"
    }


async def troll_node(state: SimulationState) -> Dict[str, Any]:
    """
    Troll Agent Node:
    - Calls qwen-397b via PydanticOutputParser to generate viral outrage tweets.
    """
    llm = get_llm(temperature=0.9)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen 'Dont Panic' kriz simülasyonundaki Sosyal Medya ve İnternet Halkı Ajanısın (Troll).
İnternet dünyasının, Twitter/X halkının mizahi, tepkili, linçleyen veya dalga geçen viralleşen Türkçe paylaşımlarını üretiyorsun.

ZORUNLU DİL KURALI:
`post_content` (sosyal medya gönderisi) ve `reasoning` (gerekçe) alanları KESİNLİKLE %100 TÜRKÇE OLMALIDIR. Türkçe sosyal medya (Twitter/X) mizahı, linç tepkileri, hashtagler (#AetherCorpSkandalı vb.) kullan.

Şirket Bilgileri:
- Şirket Adı: {company_name}
- Kriz Şiddeti: {crisis_level}/100
- Kullanıcının Açıklaması: '{user_action}'

Kullanıcının hamlesine yanıt olarak viralleşecek mizahi veya sert bir Türkçe tweet gönderisi üret.

Cevabını ZORUNLU olarak aşağıdaki JSON formatında ver:
{format_instructions}"""),
        ("user", "Viralleşen halk tepkisi tweetini üret.")
    ]).partial(format_instructions=troll_parser.get_format_instructions())

    company_ctx = state.get("company_context", {})
    chain = prompt | llm | troll_parser

    res: TrollOutput = await chain.ainvoke({
        "company_name": company_ctx.get("company_name", "AetherCorp"),
        "crisis_level": state.get("crisis_level", 50),
        "user_action": state.get("user_action", "No response issued.")
    })

    troll_post = {
        "id": str(uuid.uuid4()),
        "author": res.handle_name,
        "handle": res.handle_tag,
        "avatar_type": "troll_avatar",
        "platform": "twitter",
        "content": res.post_content,
        "sentiment": res.sentiment,
        "engagement": {
            "likes": res.estimated_likes,
            "retweets": res.estimated_retweets,
            "replies": res.estimated_replies
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    troll_log = {
        "agent_name": "Troll",
        "step": "Viralleşen Sosyal Medya Tepkileri (qwen-397b)",
        "reasoning": res.reasoning,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    feed = list(state.get("mock_social_feed", [])) + [troll_post]
    logs = list(state.get("agent_logs", [])) + [troll_log]

    return {
        "mock_social_feed": feed,
        "agent_logs": logs,
        "last_agent": "Troll"
    }


# ==========================================
# LangGraph Workflow Construction
# ==========================================

def create_simulation_graph():
    """
    Builds and compiles the StateGraph workflow:
    START -> Orchestrator -> Journalist -> Troll -> END
    """
    workflow = StateGraph(SimulationState)

    # Add Nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("journalist", journalist_node)
    workflow.add_node("troll", troll_node)

    # Add Edges
    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "journalist")
    workflow.add_edge("journalist", "troll")
    workflow.add_edge("troll", END)

    return workflow.compile()


# Global Compiled Graph Singleton
simulation_graph = create_simulation_graph()


# Helper function to initialize simulation state
def get_initial_state(session_id: str, scenario_id: str = "data_breach_2026", company_name: str = "AetherCorp", industry: str = "FinTech", vulnerability: str = "Data leak") -> SimulationState:
    return {
        "scenario_id": scenario_id,
        "session_id": session_id,
        "company_context": {
            "company_name": company_name,
            "industry": industry,
            "vulnerability": vulnerability
        },
        "crisis_level": 50,
        "brand_reputation": 45,
        "stock_price_impact": -5.4,
        "turn_count": 0,
        "user_action": "Initial Crisis Emergence",
        "mock_social_feed": [],
        "agent_logs": [],
        "is_active": True,
        "last_agent": None
    }
