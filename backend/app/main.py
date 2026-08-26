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
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            for connection in list(self.active_connections[session_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(session_id, connection)


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

            # Send initial progress signal: Turn started
            await manager.broadcast_to_session(
                session_id,
                WebSocketMessage(
                    event_type="agent_progress",
                    session_id=session_id,
                    data={
                        "step": 0,
                        "total_steps": 3,
                        "agent_name": "System",
                        "status_message": "Kriz müdahalesi yapay zeka ajanlarına iletildi. Analiz başlatılıyor...",
                        "percentage": 10
                    }
                ).model_dump()
            )

            # Run LangGraph StateGraph streaming execution node by node
            try:
                async for chunk in simulation_graph.astream(current_state, stream_mode="updates"):
                    node_name = list(chunk.keys())[0]
                    node_output = chunk[node_name]

                    # Update session state continuously
                    current_state.update(node_output)
                    active_sessions[session_id] = current_state

                    if node_name == "orchestrator":
                        await manager.broadcast_to_session(
                            session_id,
                            WebSocketMessage(
                                event_type="agent_progress",
                                session_id=session_id,
                                data={
                                    "step": 1,
                                    "total_steps": 3,
                                    "agent_name": "Orchestrator",
                                    "status_message": "1/3 Lider Strateji Ajanı (Orchestrator) kriz şiddetini ve metrikleri hesapladı.",
                                    "percentage": 33
                                }
                            ).model_dump()
                        )
                        if node_output.get("agent_logs"):
                            await manager.broadcast_to_session(
                                session_id,
                                WebSocketMessage(
                                    event_type="agent_log",
                                    session_id=session_id,
                                    data=node_output["agent_logs"][-1]
                                ).model_dump()
                            )

                    elif node_name == "journalist":
                        await manager.broadcast_to_session(
                            session_id,
                            WebSocketMessage(
                                event_type="agent_progress",
                                session_id=session_id,
                                data={
                                    "step": 2,
                                    "total_steps": 3,
                                    "agent_name": "Journalist",
                                    "status_message": "2/3 Medya & Gazeteci Ajanı son dakika kriz haberini hazırladı.",
                                    "percentage": 66
                                }
                            ).model_dump()
                        )
                        if node_output.get("agent_logs"):
                            await manager.broadcast_to_session(
                                session_id,
                                WebSocketMessage(
                                    event_type="agent_log",
                                    session_id=session_id,
                                    data=node_output["agent_logs"][-1]
                                ).model_dump()
                            )
                        if node_output.get("mock_social_feed"):
                            await manager.broadcast_to_session(
                                session_id,
                                WebSocketMessage(
                                    event_type="social_post",
                                    session_id=session_id,
                                    data=node_output["mock_social_feed"][-1]
                                ).model_dump()
                            )

                    elif node_name == "troll":
                        await manager.broadcast_to_session(
                            session_id,
                            WebSocketMessage(
                                event_type="agent_progress",
                                session_id=session_id,
                                data={
                                    "step": 3,
                                    "total_steps": 3,
                                    "agent_name": "Troll",
                                    "status_message": "3/3 Sosyal Medya Ajanı viralleşen halk tepkilerini simüle etti.",
                                    "percentage": 100
                                }
                            ).model_dump()
                        )
                        if node_output.get("agent_logs"):
                            await manager.broadcast_to_session(
                                session_id,
                                WebSocketMessage(
                                    event_type="agent_log",
                                    session_id=session_id,
                                    data=node_output["agent_logs"][-1]
                                ).model_dump()
                            )
                        if node_output.get("mock_social_feed"):
                            await manager.broadcast_to_session(
                                session_id,
                                WebSocketMessage(
                                    event_type="social_post",
                                    session_id=session_id,
                                    data=node_output["mock_social_feed"][-1]
                                ).model_dump()
                            )

            except Exception as graph_err:
                err_msg = str(graph_err)
                print(f"[Simulation Graph Execution Error]: {err_msg}")
                await manager.send_personal_message(
                    WebSocketMessage(
                        event_type="error",
                        session_id=session_id,
                        data={
                            "message": f"Simülasyon Hatası: {err_msg}",
                            "hint": "Lütfen backend/.env ayarlarını kontrol edin"
                        }
                    ).model_dump(),
                    websocket
                )
                continue

            # Stream Metrics Update
            metrics_payload = MetricsUpdateSchema(
                crisis_level=current_state["crisis_level"],
                brand_reputation=current_state["brand_reputation"],
                stock_price_impact=current_state["stock_price_impact"],
                turn_count=current_state["turn_count"],
                is_active=current_state["is_active"]
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
                        "turn_count": current_state["turn_count"],
                        "summary": f"Tur {current_state['turn_count']} başarıyla tamamlandı."
                    }
                ).model_dump()
            )

    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception as e:
        import traceback
        print(f"[WebSocket Fatal Error] Exception in session {session_id}: {str(e)}")
        traceback.print_exc()
        manager.disconnect(session_id, websocket)
