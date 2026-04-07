import { AgentSSEEvent } from "./event";

export enum SessionStatus {
    PENDING = "pending",
    RUNNING = "running",
    WAITING = "waiting",
    COMPLETED = "completed"
}

export interface CreateSessionResponse {
    session_id: string;
    estimated_cost: number;
    spent_credits: number;
    max_budget: number;
    mode: string;
    permissions: string;
    risk_level: string;
    model_tier: string;
    wide_research: boolean;
    input_mode: string;
    mode_config: Record<string, any>;
}

export interface GetSessionResponse {
    session_id: string;
    title: string | null;
    status: SessionStatus;
    events: AgentSSEEvent[];
    is_shared: boolean;
    goal: string | null;
    estimated_cost: number;
    spent_credits: number;
    max_budget: number;
    mode: string;
    permissions: string;
    risk_level: string;
    model_tier: string;
    wide_research: boolean;
    input_mode: string;
    mode_config: Record<string, any>;
}

export interface ListSessionItem {
    session_id: string;
    title: string | null;
    latest_message: string | null;
    latest_message_at: number | null;
    status: SessionStatus;
    unread_message_count: number;
    is_shared: boolean;
    estimated_cost: number;
    spent_credits: number;
    max_budget: number;
    mode: string;
    permissions: string;
    risk_level: string;
    model_tier: string;
    wide_research: boolean;
    input_mode: string;
    mode_config: Record<string, any>;
}

export interface ListSessionResponse {
    sessions: ListSessionItem[];
}

export interface ConsoleRecord {
    ps1: string;
    command: string;
    output: string;
  }
  
  export interface ShellViewResponse {
    output: string;
    session_id: string;
    console: ConsoleRecord[];
  }

export interface FileViewResponse {
    content: string;
    file: string;
}

export interface SignedUrlResponse {
    signed_url: string;
    expires_in: number;
}

export interface ShareSessionResponse {
    session_id: string;
    is_shared: boolean;
}

export interface SharedSessionResponse {
    session_id: string;
    title: string | null;
    status: SessionStatus;
    events: AgentSSEEvent[];
    is_shared: boolean;
}

export interface SessionFollowupsResponse {
    suggestions: string[];
}
  
