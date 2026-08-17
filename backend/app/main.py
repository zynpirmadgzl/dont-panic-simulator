"""
FastAPI Server & Real-Time WebSocket Router for Dont Panic.
"""
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    SimulationState,
    ScenarioInitRequest,
    UserActionRequest,
    WebSocketMessage,
    MetricsUpdateSchema
)
from app.graph import simulation_graph, get_initial_state


app = FastAPI(
    title="Dont Panic AI-Native Crisis Simulator API",
    description="Backend API & WebSocket engine for real-time crisis communication simulations.",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory session store (Replace with Redis/PostgreSQL in production)
active_sessions: Dict[str, SimulationState] = {}


# ==========================================
# WebSocket Connection Manager
# ==========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(message)


manager = ConnectionManager()


# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/")
async def root():
    return {
        "project": "Dont Panic API",
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "active_sessions_count": len(active_sessions)}


@app.get("/api/scenarios")
async def get_scenarios():
    """Return preset crisis scenario templates."""
    return [
        {
            "id": "data_breach_2026",
            "title": "Unencrypted Biometric Data Leak",
            "company_name": "AetherCorp",
            "industry": "FinTech & AI",
            "initial_crisis_level": 55,
            "description": "Hackers leaked 4 million unencrypted facial recognition hashes on a darkweb forum."
        },
        {
            "id": "ai_hallucination_scandal",
            "title": "Autonomous Medical AI Malfunction",
            "company_name": "MediPulse AI",
            "industry": "Healthcare AI",
            "initial_crisis_level": 70,
            "description": "Diagnostic AI gave contradictory dosage recommendations during trial phase."
        },
        {
            "id": "ceo_deepfake_leak",
            "title": "Viral CEO Deepfake Whistleblower",
            "company_name": "Vanguard Dynamics",
            "industry": "Defense Tech",
            "initial_crisis_level": 60,
            "description": "Synthesized audio of CEO admitting to insider trading went viral on mock Twitter."
        }
    ]


@app.post("/api/simulation/start")
async def start_simulation(req: ScenarioInitRequest):
    session_id = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    state = get_initial_state(
        session_id=session_id,
        scenario_id=req.scenario_id,
        company_name=req.company_name,
        industry=req.industry,
        vulnerability=req.vulnerability
    )
    active_sessions[session_id] = state
    return {"session_id": session_id, "state": state}


# ==========================================
# Real-Time WebSocket Route Handler
# ==========================================

@app.websocket("/ws/simulation/{session_id}")
async def websocket_simulation_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time crisis simulation turn streaming.
    Streams agent reasoning logs, mock social posts, and live metrics updates.
    """
    await manager.connect(session_id, websocket)

    # Initialize session state if missing
    if session_id not in active_sessions:
        active_sessions[session_id] = get_initial_state(session_id=session_id)

    current_state = active_sessions[session_id]

    # Send initial connection payload
    await manager.send_personal_message(
        WebSocketMessage(
            event_type="simulation_started",
            session_id=session_id,
            data={
                "message": "Connected to Dont Panic crisis engine WebSocket",
                "state": current_state
            }
        ).model_dump(),
        websocket
    )

    try:
        while True:
            # Receive free-text user action from client
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_action_text = payload.get("user_action", "").strip()

            if not user_action_text:
                await manager.send_personal_message(
                    WebSocketMessage(
                        event_type="error",
                        session_id=session_id,
                        data={"message": "user_action cannot be empty"}
                    ).model_dump(),
                    websocket
                )
                continue

            # Update current state with user action
            current_state["user_action"] = user_action_text
            initial_feed_len = len(current_state.get("mock_social_feed", []))
            initial_log_len = len(current_state.get("agent_logs", []))

            # Run LangGraph StateGraph execution
            try:
                updated_state = await simulation_graph.ainvoke(current_state)
            except Exception as graph_err:
                err_msg = str(graph_err)
                print(f"[Simulation Graph Execution Error]: {err_msg}")
                await manager.send_personal_message(
                    WebSocketMessage(
                        event_type="error",
                        session_id=session_id,
                        data={
                            "message": f"Simulation Graph Error: {err_msg}",
                            "hint": "Please check LLM_API_KEY and LLM_BASE_URL in backend/.env"
                        }
                    ).model_dump(),
                    websocket
                )
                continue

            active_sessions[session_id] = updated_state
            current_state = updated_state

            # Stream newly generated Agent Logs
            new_logs = updated_state["agent_logs"][initial_log_len:]
            for log in new_logs:
                await manager.broadcast_to_session(
                    session_id,
                    WebSocketMessage(
                        event_type="agent_log",
                        session_id=session_id,
                        data=log
                    ).model_dump()
                )
                await asyncio.sleep(0.3)  # Subtle pause for dynamic agent streaming effect

            # Stream newly generated Social Feed Posts
            new_posts = updated_state["mock_social_feed"][initial_feed_len:]
            for post in new_posts:
                await manager.broadcast_to_session(
                    session_id,
                    WebSocketMessage(
                        event_type="social_post",
                        session_id=session_id,
                        data=post
                    ).model_dump()
                )
                await asyncio.sleep(0.4)  # Streaming delay effect for social feed emergence

            # Stream Metrics Update
            metrics_payload = MetricsUpdateSchema(
                crisis_level=updated_state["crisis_level"],
                brand_reputation=updated_state["brand_reputation"],
                stock_price_impact=updated_state["stock_price_impact"],
                turn_count=updated_state["turn_count"],
                is_active=updated_state["is_active"]
            ).model_dump()

            await manager.broadcast_to_session(
                session_id,
                WebSocketMessage(
                    event_type="metrics_update",
                    session_id=session_id,
                    data=metrics_payload
                ).model_dump()
            )

            # Signal Turn Completion
            await manager.broadcast_to_session(
                session_id,
                WebSocketMessage(
                    event_type="turn_complete",
                    session_id=session_id,
                    data={
                        "turn_count": updated_state["turn_count"],
                        "summary": f"Turn {updated_state['turn_count']} processed successfully"
                    }
                ).model_dump()
            )

    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception as e:
        manager.disconnect(session_id, websocket)
        print(f"[WebSocket Error] Exception in session {session_id}: {str(e)}")
