import { create } from "zustand";

export interface SocialPost {
  id: string;
  author: string;
  handle: string;
  avatar_type?: string;
  platform: "twitter" | "news" | "reddit" | "press";
  content: string;
  sentiment: "negative" | "positive" | "neutral" | "outrage" | "panic";
  engagement: {
    likes: number;
    retweets: number;
    replies: number;
  };
  timestamp: string;
}

export interface AgentLog {
  agent_name: string;
  step: string;
  reasoning: string;
  metrics_delta?: {
    crisis_level_delta?: number;
    brand_reputation_delta?: number;
    stock_price_impact_delta?: number;
  };
  timestamp: string;
}

export interface TelemetryPoint {
  turn: number;
  crisis_level: number;
  brand_reputation: number;
  stock_price_impact: number;
}

export interface SimulationStoreState {
  session_id: string;
  scenario_id: string;
  company_name: string;
  industry: string;
  vulnerability: string;

  crisis_level: number;
  brand_reputation: number;
  stock_price_impact: number;
  turn_count: number;
  is_active: boolean;
  is_processing: boolean;

  user_action_input: string;
  mock_social_feed: SocialPost[];
  agent_logs: AgentLog[];
  telemetry_history: TelemetryPoint[];

  error_message: string | null;
  ws_connected: boolean;
  progress_status: { step: number; total_steps: number; status_message: string; percentage: number } | null;

  // Actions
  setSession: (sessionId: string, companyName: string, industry: string, vulnerability: string, scenarioId?: string) => void;
  setUserActionInput: (input: string) => void;
  setIsProcessing: (status: boolean) => void;
  setProgressStatus: (status: { step: number; total_steps: number; status_message: string; percentage: number } | null) => void;
  setWsConnected: (connected: boolean) => void;
  appendAgentLog: (log: AgentLog) => void;
  appendSocialPost: (post: SocialPost) => void;
  updateMetrics: (metrics: { crisis_level: number; brand_reputation: number; stock_price_impact: number; turn_count: number; is_active: boolean }) => void;
  setError: (msg: string | null) => void;
  hydrateState: (state: any) => void;
  resetSession: () => void;
}

export const useSimulationStore = create<SimulationStoreState>((set) => ({
  session_id: "test_session_interactive",
  scenario_id: "data_breach_2026",
  company_name: "AetherCorp",
  industry: "FinTech & Yapay Zeka",
  vulnerability: "Şifrelenmemiş müşteri biyometrik veri sızıntısı",

  crisis_level: 50,
  brand_reputation: 45,
  stock_price_impact: -5.4,
  turn_count: 0,
  is_active: true,
  is_processing: false,
  progress_status: null,

  user_action_input: "",
  mock_social_feed: [],
  agent_logs: [],
  telemetry_history: [
    { turn: 0, crisis_level: 50, brand_reputation: 45, stock_price_impact: -5.4 }
  ],

  error_message: null,
  ws_connected: false,

  setSession: (sessionId, companyName, industry, vulnerability, scenarioId = "data_breach_2026") =>
    set({
      session_id: sessionId,
      scenario_id: scenarioId,
      company_name: companyName,
      industry: industry,
      vulnerability: vulnerability,
      crisis_level: 50,
      brand_reputation: 45,
      stock_price_impact: -5.4,
      turn_count: 0,
      is_active: true,
      user_action_input: "",
      mock_social_feed: [],
      agent_logs: [],
      telemetry_history: [{ turn: 0, crisis_level: 50, brand_reputation: 45, stock_price_impact: -5.4 }],
      error_message: null,
      progress_status: null
    }),

  setUserActionInput: (input) => set({ user_action_input: input }),

  setIsProcessing: (status) =>
    set((state) => ({
      is_processing: status,
      progress_status: status ? state.progress_status : null
    })),

  setProgressStatus: (status) => set({ progress_status: status }),

  setWsConnected: (connected) => set({ ws_connected: connected }),

  appendAgentLog: (log) =>
    set((state) => ({
      agent_logs: [log, ...state.agent_logs]
    })),

  appendSocialPost: (post) =>
    set((state) => ({
      mock_social_feed: [post, ...state.mock_social_feed]
    })),

  updateMetrics: (metrics) =>
    set((state) => {
      const newPoint: TelemetryPoint = {
        turn: metrics.turn_count,
        crisis_level: metrics.crisis_level,
        brand_reputation: metrics.brand_reputation,
        stock_price_impact: metrics.stock_price_impact
      };
      return {
        crisis_level: metrics.crisis_level,
        brand_reputation: metrics.brand_reputation,
        stock_price_impact: metrics.stock_price_impact,
        turn_count: metrics.turn_count,
        is_active: metrics.is_active,
        telemetry_history: [...state.telemetry_history, newPoint]
      };
    }),

  setError: (msg) => set({ error_message: msg, is_processing: false }),

  hydrateState: (incomingState) =>
    set({
      crisis_level: incomingState.crisis_level ?? 50,
      brand_reputation: incomingState.brand_reputation ?? 45,
      stock_price_impact: incomingState.stock_price_impact ?? -5.4,
      turn_count: incomingState.turn_count ?? 0,
      mock_social_feed: incomingState.mock_social_feed || [],
      agent_logs: incomingState.agent_logs || []
    }),

  resetSession: () =>
    set({
      turn_count: 0,
      crisis_level: 50,
      brand_reputation: 45,
      stock_price_impact: -5.4,
      mock_social_feed: [],
      agent_logs: [],
      telemetry_history: [{ turn: 0, crisis_level: 50, brand_reputation: 45, stock_price_impact: -5.4 }],
      error_message: null,
      is_processing: false
    })
}));
