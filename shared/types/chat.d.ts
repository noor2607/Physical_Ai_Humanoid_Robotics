// Shared TypeScript interfaces for chat functionality
// Based on data model defined in specs/001-docusaurus-fastapi-integration/data-model.md

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  context?: string;
}

export interface ChatRequest {
  query: string;
  context?: string;
  sessionId?: string;
}

export interface ChatResponse {
  response: string;
  sources?: string[];
  error?: ChatError;
}

export interface ChatError {
  type: string;
  message: string;
  code?: number;
}

export interface ChatContext {
  selectedText: string;
  pageUrl: string;
  pageTitle?: string;
}