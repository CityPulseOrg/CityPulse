// Status values matching backend ReportStatus enum
export type ReportStatus = "New" | "In Progress" | "Resolved" | "Waiting for user follow-up";

// Priority values matching backend
export type ReportPriority = "not_urgent" | "urgent" | "very_urgent" | "Low" | "Medium" | "High";

// Severity values matching backend
export type ReportSeverity = "very_low" | "low" | "medium" | "high" | "very_high";

export interface ClarificationQuestion {
  id: string;
  question: string;
  type: "text" | "choice";
  choices?: string[];
}

export interface Image {
  id: string;
  url: string;
}

export interface ReportEvent {
  id: string;
  report_id: string;
  event_type: string;
  payload?: string;
  creation_time: string;
}

export interface CreateIssueResponse {
  id: string;
  status: ReportStatus;
  title?: string;
  clarification_questions?: ClarificationQuestion[];
  images?: Image[];
}

export interface IssueDetails {
  id: string;
  status: ReportStatus;
  title?: string;
  description: string;
  category?: string;
  priority?: string;
  severity?: string;
  department?: string;
  images: Image[];
  clarification_questions?: ClarificationQuestion[];
  events?: ReportEvent[];
}

export interface FollowupRequest {
  answers: { [questionId: string]: string };
}

export interface UpdateStatusRequest {
  report_id: string;
  status: ReportStatus;
}