"use client";

import { useEffect, useCallback } from "react";
import { useSimulationStore } from "@/store/useSimulationStore";

// Singleton WebSocket references outside React component tree
let globalSocket: WebSocket | null = null;
let reconnectTimer: NodeJS.Timeout | null = null;
let currentSessionId: string | null = null;

function connectWebSocket(sessionId: string) {
  if (!sessionId) return;

  // If already connected or connecting to the same session, do nothing
  if (
    globalSocket &&
    currentSessionId === sessionId &&
    (globalSocket.readyState === WebSocket.OPEN || globalSocket.readyState === WebSocket.CONNECTING)
  ) {
    return;
  }

  // Clear previous reconnect timer if active
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  // Detach previous listeners and close old socket if switching sessions or dead
  if (globalSocket) {
    globalSocket.onopen = null;
    globalSocket.onmessage = null;
    globalSocket.onerror = null;
    globalSocket.onclose = null;
    if (globalSocket.readyState === WebSocket.OPEN || globalSocket.readyState === WebSocket.CONNECTING) {
      globalSocket.close();
    }
    globalSocket = null;
  }

  currentSessionId = sessionId;
  const wsUrl = `ws://127.0.0.1:8000/ws/simulation/${sessionId}`;
  console.log(`[WebSocket Singleton] Connecting to ${wsUrl}...`);

  const ws = new WebSocket(wsUrl);
  globalSocket = ws;

  ws.onopen = () => {
    console.log(`[WebSocket Singleton] Connected to session ${sessionId}`);
    useSimulationStore.getState().setWsConnected(true);
    useSimulationStore.getState().setError(null);
  };

  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      const { event_type, data } = payload;
      const store = useSimulationStore.getState();

      switch (event_type) {
        case "simulation_started":
          console.log("[WebSocket Event] simulation_started", data);
          store.setWsConnected(true);
          if (data?.state) {
            store.hydrateState(data.state);
          }
          break;

        case "agent_progress":
          console.log("[WebSocket Event] agent_progress", data);
          store.setProgressStatus(data);
          break;

        case "agent_log":
          console.log("[WebSocket Event] agent_log", data);
          store.appendAgentLog(data);
          break;

        case "social_post":
          console.log("[WebSocket Event] social_post", data);
          store.appendSocialPost(data);
          break;

        case "metrics_update":
          console.log("[WebSocket Event] metrics_update", data);
          store.updateMetrics(data);
          break;

        case "turn_complete":
          console.log("[WebSocket Event] turn_complete", data);
          store.setIsProcessing(false);
          store.setProgressStatus(null);
          break;

        case "error":
          console.error("[WebSocket Event Error]", data);
          store.setError(data.message || "An unknown simulation error occurred.");
          store.setIsProcessing(false);
          store.setProgressStatus(null);
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
    useSimulationStore.getState().setWsConnected(false);
  };

  ws.onclose = () => {
    console.log("[WebSocket Singleton Closed]");
    useSimulationStore.getState().setWsConnected(false);

    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      if (currentSessionId) {
        connectWebSocket(currentSessionId);
      }
    }, 3000);
  };
}

export function useWebSocket(sessionId: string) {
  useEffect(() => {
    connectWebSocket(sessionId);
    // Intentionally do NOT close globalSocket in cleanup so React re-renders never disconnect
  }, [sessionId]);

  const sendAction = useCallback((userAction: string) => {
    const store = useSimulationStore.getState();

    if (!globalSocket || globalSocket.readyState !== WebSocket.OPEN) {
      store.setError("WebSocket bağlantısı aktif değil. Lütfen backend servisinin çalıştığından emin olun.");
      return false;
    }

    store.setIsProcessing(true);
    store.setError(null);

    const payload = { user_action: userAction };
    globalSocket.send(JSON.stringify(payload));
    return true;
  }, []);

  return {
    sendAction,
    isConnected: globalSocket?.readyState === WebSocket.OPEN
  };
}
