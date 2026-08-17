"""
Unit tests for LangGraph StateGraph nodes, transitions, and FastAPI WebSocket endpoints with qwen-397b LLM mocking.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app
from app.graph import simulation_graph, get_initial_state
from app.schemas import OrchestratorOutput, JournalistOutput, TrollOutput

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_scenarios_endpoint():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert isinstance(scenarios, list)
    assert len(scenarios) >= 3
    assert scenarios[0]["id"] == "data_breach_2026"


def test_start_simulation_endpoint():
    payload = {
        "scenario_id": "data_breach_2026",
        "company_name": "TestCorp",
        "industry": "Cybersecurity",
        "vulnerability": "API secret key leaked on GitHub"
    }
    response = client.post("/api/simulation/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["state"]["company_context"]["company_name"] == "TestCorp"


@pytest.mark.asyncio
async def test_langgraph_workflow_execution_with_llm():
    initial_state = get_initial_state(
        session_id="test_session_1",
        scenario_id="data_breach_2026",
        company_name="AetherCorp"
    )
    initial_state["user_action"] = "We sincerely apologize for the data leak and are providing free credit monitoring."

    mock_orch = OrchestratorOutput(
        reasoning="qwen-397b evaluated proactive ownership in press release.",
        crisis_level_delta=-10,
        brand_reputation_delta=12,
        stock_price_impact_delta=3.5
    )

    mock_journo = JournalistOutput(
        outlet_name="TechChronicle Daily",
        outlet_handle="@TechChronicle",
        headline="DEVELOPING: AetherCorp promises free credit monitoring following breach.",
        sentiment="positive",
        reasoning="Media framed transparent ownership favorably.",
        estimated_likes=12000,
        estimated_retweets=4500,
        estimated_replies=1200
    )

    mock_troll = TrollOutput(
        handle_name="Silicon Outrage",
        handle_tag="@TechHater99",
        post_content="Free credit monitoring isn't enough for 4M leaked hashes 💀 #DontPanic",
        sentiment="outrage",
        reasoning="Viral mob remains skeptical of corporate apology.",
        estimated_likes=35000,
        estimated_retweets=11000,
        estimated_replies=4200
    )

    from langchain_core.runnables import RunnableLambda

    def make_mock_llm(output_obj):
        async def _mock_invoke(prompt_input, *args, **kwargs):
            return AIMessage(content=output_obj.model_dump_json())
        return RunnableLambda(_mock_invoke)

    # Mock get_llm output for PydanticOutputParser
    with patch("app.graph.get_llm") as mock_get_llm:
        def mock_get_llm_side_effect(temperature=0.7):
            # Inspect stack / caller if needed or return dynamic Runnable
            mock_llm = MagicMock()
            if temperature == 0.3:
                return make_mock_llm(mock_orch)
            elif temperature == 0.7:
                return make_mock_llm(mock_journo)
            elif temperature == 0.9:
                return make_mock_llm(mock_troll)
            return make_mock_llm(mock_orch)

        mock_get_llm.side_effect = mock_get_llm_side_effect

        # Invoke LangGraph workflow
        final_state = await simulation_graph.ainvoke(initial_state)

        # Assert turn count incremented
        assert final_state["turn_count"] == 1

        # Assert agent logs were populated with qwen-397b reasoning
        logs = final_state["agent_logs"]
        assert len(logs) == 3
        assert "qwen-397b evaluated proactive ownership" in logs[0]["reasoning"]
        assert "Media framed transparent ownership" in logs[1]["reasoning"]
        assert "Viral mob remains skeptical" in logs[2]["reasoning"]

        # Assert mock social feed received live structured posts
        assert len(final_state["mock_social_feed"]) == 2
        assert final_state["mock_social_feed"][0]["author"] == "TechChronicle Daily"
        assert final_state["mock_social_feed"][1]["author"] == "Silicon Outrage"
        assert final_state["last_agent"] == "Troll"
