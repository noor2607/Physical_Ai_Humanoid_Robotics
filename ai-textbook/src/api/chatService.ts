/**
 * Service for handling chat API communication
 */
export interface ChatRequest {
  query: string;
  context?: string;
  sessionId?: string;
}

export interface ChatResponse {
  response: string;
  sources?: string[];
  error?: ChatError;
  sessionId?: string;
  success?: boolean;
}

export interface ChatError {
  type: string;
  message: string;
  code?: number;
}

// API base URL - Updated to match backend API structure
// Using absolute path to connect directly to backend
const API_BASE_URL = 'http://localhost:8000'; // Direct connection to backend server

/**
 * Send a chat query to the backend API
 */
export const sendChatQuery = async (
  query: string,
  context?: string,
  sessionId?: string
): Promise<ChatResponse> => {
  try {
    const request = {
      question: query,
      selected_text: context, // Use selected text as context (bypasses Qdrant)
    };

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail?.error?.message ||
        errorData.detail ||
        `HTTP error! status: ${response.status}`
      );
    }

    const data = await response.json();

    // Transform backend response to match frontend expectations
    const transformedResponse: ChatResponse = {
      response: data.answer || data.response, // Backend returns 'answer' field, not 'response'
      success: data.success ?? true, // Use success field from backend or assume success
      error: undefined,
      sources: data.sources || [], // Use sources from backend if available
      sessionId: sessionId
    };

    return transformedResponse;
  } catch (error) {
    console.error('Error sending chat query:', error);
    throw error;
  }
};

/**
 * Check if the backend API is healthy
 */
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Error checking API health:', error);
    return false;
  }
};