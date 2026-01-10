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

export interface CreateIssueResponse {
  id: string;
  status: string;
  clarification_questions?: ClarificationQuestion[];
  images?: Image[];
}

export interface IssueDetails {
  id: string;
  status: string;
  description: string;
  category?: string;
  priority?: string;
  department?: string;
  images: Image[];
  clarification_questions?: ClarificationQuestion[];
  events?: any[];
}

export interface FollowupRequest {
  answers: { [questionId: string]: string };
}

export interface UpdateStatusRequest {
  status: string;
}