// User and Auth types
export interface User {
  id: string;
  email: string;
  workspace_id: string;
  role: string;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

// Workspace types
export interface Workspace {
  id: string;
  name: string;
  owner_id: string;
  settings: Record<string, any>;
  created_at: string;
}

// Campaign types
export interface Brief {
  goal: string;
  audiences: string[];
  offer: string;
  competitors: string[];
  channels: string[];
  budget_band: string;
  voice_constraints?: string;
}

export interface Campaign {
  id: string;
  workspace_id: string;
  name: string;
  status: string;
  brief: Brief;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  name: string;
  brief: Brief;
}

// Signal types
export interface Signal {
  id: string;
  campaign_id: string;
  source: string;
  search_method: string;
  query: string;
  evidence: any[];
  relevance_score: number;
  created_at: string;
}

export interface CollectSignalsRequest {
  cartridge_names?: string[];
  max_queries_per_cartridge: number;
}

export interface CollectSignalsResponse {
  campaign_id: string;
  cartridges_run: number;
  total_signals: number;
  errors: any[];
  timestamp: string;
}

// Analysis types
export type AnalysisType = 'comprehensive' | 'competitor' | 'audience' | 'messaging' | 'creative' | 'trends';
export type LLMProvider = 'claude' | 'openai';
export type AnalysisStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface AnalyzeRequest {
  analysis_type: AnalysisType;
  llm_provider: LLMProvider;
  max_signals?: number;
  min_relevance: number;
  async_mode: boolean;
}

export interface SignalAnalysis {
  id: string;
  campaign_id: string;
  analysis_type: string;
  status: string;
  llm_provider?: string;
  llm_model?: string;
  tokens_used?: number;
  insights?: any;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

// Strategic Brief types
export interface GenerateBriefRequest {
  llm_provider: LLMProvider;
  include_analysis_ids?: string[];
  custom_instructions?: string;
  async_mode: boolean;
}

export interface StrategicBrief {
  id: string;
  campaign_id: string;
  status: string;
  version: number;
  content: any;
  custom_instructions?: string;
  llm_provider?: string;
  llm_model?: string;
  tokens_used?: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

// Audience Insights types
export interface AudienceInsightsRequest {
  llm_provider: LLMProvider;
  focus_areas?: string[];
}

export interface AudienceInsights {
  campaign_id: string;
  insights: any;
  metadata: {
    analyses_used: number;
    llm_provider: string;
    llm_model: string;
    tokens_used: number;
  };
}
