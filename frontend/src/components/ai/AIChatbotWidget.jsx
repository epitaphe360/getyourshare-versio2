import React, { useState, useEffect, useRef } from 'react';
import { aiAPI } from '../../services/newEndpointsAPI';
import './AIRecommendations.css';

const AIChatbotWidget = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Generate unique session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);

    // Load chat history if exists
    loadChatHistory(newSessionId);

    // Add welcome message
    setMessages([
      {
        role: 'bot',
        content: "👋 Hi! I'm your AI shopping assistant. I can help you find products, answer questions, and provide recommendations. How can I help you today?",
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async (sid) => {
    try {
      const response = await aiAPI.getChatbotHistory(sid);
      if (response.data?.history && response.data.history.length > 0) {
        setMessages(response.data.history);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await aiAPI.chatWithBot(inputMessage, sessionId);

      const botMessage = {
        role: 'bot',
        content: response.data?.response || "I'm sorry, I couldn't process that. Could you try rephrasing?",
        timestamp: new Date().toISOString(),
        suggestions: response.data?.suggestions || [],
        products: response.data?.recommended_products || [],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        role: 'bot',
        content: "Sorry, I'm having trouble connecting. Please try again in a moment.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  if (!isOpen) return null;

  return (
    <div className="ai-chatbot">
      <div className="chatbot-header">
        <div>
          <h3>🤖 AI Shopping Assistant</h3>
          <span style={{ fontSize: '12px', opacity: 0.9 }}>Always here to help</span>
        </div>
        <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' }}>
          ×
        </button>
      </div>

      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.content}
              {message.products && message.products.length > 0 && (
                <div className="recommended-products" style={{ marginTop: '10px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '5px' }}>
                    Recommended Products:
                  </div>
                  {message.products.map((product, idx) => (
                    <div key={idx} style={{
                      padding: '8px',
                      background: '#f5f5f5',
                      borderRadius: '6px',
                      marginBottom: '5px',
                      fontSize: '13px'
                    }}>
                      <div style={{ fontWeight: 'bold' }}>{product.name}</div>
                      <div style={{ color: '#1976d2' }}>${product.price}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div style={{ fontSize: '10px', color: '#999', marginTop: '4px' }}>
              {formatTime(message.timestamp)}
            </div>
            {message.suggestions && message.suggestions.length > 0 && (
              <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                {message.suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(suggestion)}
                    style={{
                      padding: '4px 8px',
                      fontSize: '11px',
                      background: '#e3f2fd',
                      border: '1px solid #1976d2',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      color: '#1976d2',
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message bot">
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

      <form onSubmit={handleSendMessage} className="chatbot-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !inputMessage.trim()}>
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default AIChatbotWidget;
