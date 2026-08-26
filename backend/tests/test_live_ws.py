"""
Live Interactive WebSocket Test Script for Dont Panic Backend
Run this script while `uvicorn app.main:app --port 8000` is running.
"""
import asyncio
import json
import websockets

async def test_simulation():
    uri = "ws://localhost:8000/ws/simulation/test_session_interactive"
    print(f"Connecting to WebSocket at {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            # 1. Connection confirmation
            init_msg = await websocket.recv()
            print("\n[CONNECTED] Initial payload received:")
            print(json.dumps(json.loads(init_msg), indent=2))

            # 2. Send user crisis response move
            user_move = {
                "user_action": "We sincerely apologize for the data leak, have patched the security vulnerability, and offer 2 years of free credit protection to all affected users."
            }
            print(f"\n[SENDING USER ACTION]: '{user_move['user_action']}'\n")
            await websocket.send(json.dumps(user_move))

            # 3. Stream dynamic events from qwen-397b multi-agent graph
            print("--- STREAMING LIVE AGENT RESPONSES ---")
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                event_type = data.get("event_type")

                if event_type == "error":
                    err = data.get("data", {})
                    print(f"⚠️ [API KEY ERROR]: {err.get('message')}")
                    print(f"💡 {err.get('hint', '')}")
                    break

                elif event_type == "agent_log":
                    log = data.get("data", {})
                    print(f"🤖 [{log.get('agent_name')}] ({log.get('step')}): {log.get('reasoning')}")
                    if log.get("metrics_delta"):
                        print(f"   📊 Metrics Shift: {log.get('metrics_delta')}")

                elif event_type == "social_post":
                    post = data.get("data", {})
                    print(f"💬 [{post.get('platform').upper()}] {post.get('author')} ({post.get('handle')}):")
                    print(f"   \"{post.get('content')}\" [Sentiment: {post.get('sentiment')}]")

                elif event_type == "metrics_update":
                    m = data.get("data", {})
                    print(f"\n📈 [UPDATED METRICS] Crisis: {m.get('crisis_level')}/100 | Reputation: {m.get('brand_reputation')}/100 | Stock Impact: {m.get('stock_price_impact')}%\n")

                elif event_type == "turn_complete":
                    print("✅ Turn completed successfully!")
                    break

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the Uvicorn server is running: ./venv/bin/uvicorn app.main:app --port 8000")

if __name__ == "__main__":
    asyncio.run(test_simulation())
