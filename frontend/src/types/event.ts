import type { FileInfo } from '../api/file';

export type AgentSSEEvent = {
  event: 'tool' | 'step' | 'message' | 'error' | 'done' | 'title' | 'wait' | 'plan' | 'attachments' | 'wide_research_subjects_identified' | 'wide_research_subject_complete' | 'wide_research_complete';
  data: ToolEventData | StepEventData | MessageEventData | ErrorEventData | DoneEventData | TitleEventData | WaitEventData | PlanEventData | WideResearchSubjectsIdentifiedEventData | WideResearchSubjectCompleteEventData | WideResearchCompleteEventData;
}

export interface BaseEventData {
  event_id: string;
  timestamp: number;
}

export interface ToolEventData extends BaseEventData {
  tool_call_id: string;
  name: string;
  status: "calling" | "called";
  function: string;
  args: {[key: string]: any};
  content?: any;
}

export interface StepEventData extends BaseEventData {
  status: "pending" | "running" | "completed" | "failed"
  id: string
  description: string
}

export interface MessageEventData extends BaseEventData {
  content: string;
  role: "user" | "assistant";
  attachments: FileInfo[];
}

export interface ErrorEventData extends BaseEventData {
  error: string;
}

export interface DoneEventData extends BaseEventData {
}

export interface WaitEventData extends BaseEventData {
}

export interface TitleEventData extends BaseEventData {
  title: string;
}

export interface PlanEventData extends BaseEventData {
  steps: StepEventData[];
}

export interface WideResearchSubjectsIdentifiedEventData extends BaseEventData {
  query: string;
  subjects: string[];
}

export interface WideResearchSubjectCompleteEventData extends BaseEventData {
  query: string;
  index: number;
  total: number;
  completed: number;
  subject: Record<string, any>;
}

export interface WideResearchCompleteEventData extends BaseEventData {
  query: string;
  report: string;
  files: FileInfo[];
  subjects: Record<string, any>[];
}
