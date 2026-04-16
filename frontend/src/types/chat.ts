export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
}

export interface Citation {
  source: string;
  page?: number;
  section?: string;
}
