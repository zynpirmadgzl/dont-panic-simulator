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
        ("system", """You are the Lead Crisis Orchestrator Agent for 'Dont Panic', an AI-native high-stakes corporate crisis simulation platform.
Your job is to evaluate the user's PR press release, tweet, or tactical move in response to an escalating crisis.

Target Company Context:
- Name: {company_name}
- Industry: {industry}
- Vulnerability / Backstory: {vulnerability}

Current Metrics:
- Crisis Severity Level: {crisis_level}/100 (0 is peace, 100 is total collapse)
- Brand Reputation Score: {brand_reputation}/100
- Stock Market Impact: {stock_price_impact}%
- Turn Number: {turn_count}

Assess the user's action objectively. Determine the impact deltas:
- crisis_level_delta: integer between -30 (huge cooling) and +30 (catastrophic escalation)
- brand_reputation_delta: integer between -30 and +30
- stock_price_impact_delta: float between -15.0 and +10.0

Be rigorous. Weak, tone-deaf, or defensive statements should severely worsen metrics.

IMPORTANT: You MUST format your response as a valid JSON object matching the following instructions:
{format_instructions}"""),
        ("user", "User Action / Tactical Move: {user_action}")
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
        "step": f"Turn {turn_count} Strategic Evaluation (qwen-397b)",
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
        ("system", """You are the Journalist Agent in 'Dont Panic', an AI crisis simulator.
You represent elite tech and business news media outlets (e.g., TechChronicle Daily, Apex Business Wire, Bloomberg Tech, MarketPulse).

Company Context:
- Company: {company_name}
- Current Crisis Severity: {crisis_level}/100
- User's Latest Press Release / Response: '{user_action}'

Generate an authoritative news headline or article snippet reacting to the situation.

IMPORTANT: You MUST format your response as a valid JSON object matching the following instructions:
{format_instructions}"""),
        ("user", "Draft breaking news coverage.")
    ]).partial(format_instructions=journalist_parser.get_format_instructions())

    company_ctx = state.get("company_context", {})
    chain = prompt | llm | journalist_parser

    res: JournalistOutput = await chain.ainvoke({
        "company_name": company_ctx.get("company_name", "AetherCorp"),
        "crisis_level": state.get("crisis_level", 50),
        "user_action": state.get("user_action", "No response issued.")
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
        "step": "Media Framing Analysis (qwen-397b)",
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
        ("system", """You are the Troll Agent representing the unscripted, chaotic internet mob in 'Dont Panic'.
You craft viral, sarcastic, meme-heavy, and savage tweets with hashtags reacting to corporate crisis blunders or PR announcements.

Company Context:
- Target Company: {company_name}
- Current Crisis Severity: {crisis_level}/100
- User PR Move: '{user_action}'

Create an engaging, viral social post from an anonymous handle or tech critic.

IMPORTANT: You MUST format your response as a valid JSON object matching the following instructions:
{format_instructions}"""),
        ("user", "Generate viral public tweet.")
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
        "step": "Viral Mob Dynamics Generation (qwen-397b)",
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
