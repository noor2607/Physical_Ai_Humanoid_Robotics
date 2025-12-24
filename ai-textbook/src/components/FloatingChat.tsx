import React, { useState, useEffect, useRef } from 'react';
import './FloatingChat.css';
import { sendChatQuery, ChatResponse, ChatError } from '../api/chatService';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const FloatingChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Function to get selected text from the page
  const getSelectedText = (): string => {
    const selection = window.getSelection();
    return selection ? selection.toString().trim() : '';
  };

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    // Get selected text as context if available
    const selectedText = getSelectedText();

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setError(null);

    try {
      // Call the backend API using the service
      const data: ChatResponse = await sendChatQuery(inputText, selectedText, sessionId);

      // Update session ID if returned
      if (data.sessionId && !sessionId) {
        setSessionId(data.sessionId);
      }

      // Add AI response to chat
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      // Show sources if available
      if (data.sources && data.sources.length > 0) {
        const sourcesMessage: ChatMessage = {
          id: (Date.now() + 2).toString(),
          text: `Sources: ${data.sources.join(', ')}`,
          sender: 'ai',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, sourcesMessage]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while sending the message');

      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: `Error: ${err instanceof Error ? err.message : 'An error occurred while sending the message'}`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle key press (Enter to send)
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Toggle chat window
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Clear chat
  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="floating-chat">
      {isOpen ? (
        <div className="chat-window">
          <div className="chat-header">
            <h3>AI Assistant</h3>
            <div className="chat-header-actions">
              <button onClick={clearChat} className="clear-btn" title="Clear chat">
                ✕
              </button>
              <button onClick={toggleChat} className="close-btn" title="Close chat">
                −
              </button>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics course.</p>
                <p>Ask me anything about the course content, or select text on the page to provide context.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.sender}-message`}
                >
                  <div className="message-content">
                    {message.text}
                  </div>
                  <div className="message-timestamp">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="message ai-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            {error && <div className="error-message">{error}</div>}
            <div className="input-container">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about the course content..."
                className="chat-input"
                rows={2}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading}
                className="send-button"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <button className="chat-toggle-button" onClick={toggleChat}>
          <span>🤖</span>
        </button>
      )}
    </div>
  );
};

export default FloatingChat;