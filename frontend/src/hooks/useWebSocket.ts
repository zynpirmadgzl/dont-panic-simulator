"use client";

import { useEffect, useRef, useCallback } from "react";
import { useSimulationStore } from "@/store/useSimulationStore";

export function useWebSocket(sessionId: string) {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);

  const {
    setWsConnected,
    appendAgentLog,
    appendSocialPost,
    updateMetrics,
    setIsProcessing,
    setError
  } = useSimulationStore();

  const connect = useCallback(() => {
    if (!sessionId) return;

    // Clean existing socket
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsUrl = `ws://127.0.0.1:8000/ws/simulation/${sessionId}`;
    console.log(`[WebSocket] Connecting to ${wsUrl}...`);

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`[WebSocket] Connected to session ${sessionId}`);
      setWsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event_type, data } = payload;

        switch (event_type) {
          case "simulation_started":
            console.log("[WebSocket Event] simulation_started", data);
            setWsConnected(true);
            break;

          case "agent_log":
            console.log("[WebSocket Event] agent_log", data);
            appendAgentLog(data);
            break;

          case "social_post":
            console.log("[WebSocket Event] social_post", data);
            appendSocialPost(data);
            break;

          case "metrics_update":
            console.log("[WebSocket Event] metrics_update", data);
            updateMetrics(data);
            break;

          case "turn_complete":
            console.log("[WebSocket Event] turn_complete", data);
            setIsProcessing(false);
            break;

          case "error":
            console.error("[WebSocket Event Error]", data);
            setError(data.message || "An unknown simulation error occurred.");
            setIsProcessing(false);
            break;

          default:
            console.log("[WebSocket Event Unknown]", payload);
        }
      } catch (err) {
        console.error("[WebSocket Parsing Error]", err);
      }
    };

    ws.onerror = (error) => {
      console.warn("[WebSocket Connection Warning]", error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log("[WebSocket Closed]");
      setWsConnected(false);
      // Attempt auto-reconnect after 3 seconds
      reconnectTimerRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };
  }, [sessionId, setWsConnected, appendAgentLog, appendSocialPost, updateMetrics, setIsProcessing, setError]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  const sendAction = useCallback(
    (userAction: string) => {
      if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
        setError("WebSocket is not connected. Make sure Uvicorn server is running on port 8000.");
        return false;
      }

      setIsProcessing(true);
      setError(null);

      const payload = { user_action: userAction };
      socketRef.current.send(JSON.stringify(payload));
      return true;
    },
    [setIsProcessing, setError]
  );

  return { sendAction, isConnected: socketRef.current?.readyState === WebSocket.OPEN };
}
