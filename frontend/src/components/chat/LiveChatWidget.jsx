import React, { useState, useEffect, useRef } from 'react';
import { liveChatAPI } from '../../services/newEndpointsAPI';
import './LiveChat.css';

const LiveChatWidget = ({ userId, userRole = 'customer' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentRoom, setCurrentRoom] = useState(null);
  const [typing, setTyping] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  useEffect(() => {
    if (isOpen && !isConnected && userId) {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isOpen, userId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isOpen && messages.length > 0) {
      const unread = messages.filter(m => !m.read && m.sender_id !== userId).length;
      setUnreadCount(unread);
    }
  }, [messages, isOpen, userId]);

  const connectWebSocket = () => {
    try {
      const wsURL = liveChatAPI.getWebSocketURL(userId);
      const ws = new WebSocket(wsURL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);

        // Send authentication message
        ws.send(JSON.stringify({
          type: 'auth',
          user_id: userId,
          role: userRole,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (isOpen) {
            connectWebSocket();
          }
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'message':
        setMessages(prev => [...prev, {
          id: data.message_id || Date.now(),
          content: data.content,
          sender_id: data.sender_id,
          sender_name: data.sender_name,
          timestamp: data.timestamp || new Date().toISOString(),
          read: isOpen,
        }]);
        if (!isOpen) {
          setUnreadCount(prev => prev + 1);
        }
        break;

      case 'typing':
        if (data.sender_id !== userId) {
          setTyping(true);
          if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
          }
          typingTimeoutRef.current = setTimeout(() => setTyping(false), 3000);
        }
        break;

      case 'room_joined':
        setCurrentRoom(data.room_id);
        if (data.history) {
          setMessages(data.history);
        }
        break;

      case 'online_users':
        setOnlineUsers(data.users || []);
        break;

      case 'user_joined':
      case 'user_left':
        // Handle user presence updates
        console.log(`User ${data.type}:`, data.user_id);
        break;

      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !isConnected) return;

    const message = {
      type: 'message',
      content: inputMessage,
      room_id: currentRoom,
      sender_id: userId,
      timestamp: new Date().toISOString(),
    };

    // Send via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));

      // Add to local messages immediately for instant feedback
      setMessages(prev => [...prev, {
        ...message,
        id: Date.now(),
        sender_name: 'You',
        read: true,
      }]);

      setInputMessage('');
    } else {
      console.error('WebSocket is not connected');
      alert('Connection lost. Attempting to reconnect...');
      connectWebSocket();
    }
  };

  const sendTypingIndicator = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        sender_id: userId,
        room_id: currentRoom,
      }));
    }
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    sendTypingIndicator();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setUnreadCount(0);
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button className="chat-toggle-btn" onClick={toggleChat}>
        💬
        {unreadCount > 0 && (
          <span className="unread-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="live-chat-widget">
          <div className="chat-header">
            <div className="header-info">
              <h3>Live Support</h3>
              <div className="connection-status">
                <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
                <span>{isConnected ? 'Connected' : 'Connecting...'}</span>
              </div>
            </div>
            <div className="header-actions">
              {onlineUsers.length > 0 && (
                <span className="online-count" title="Online agents">
                  👥 {onlineUsers.length}
                </span>
              )}
              <button onClick={toggleChat} className="close-btn">✖</button>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <div className="welcome-icon">👋</div>
                <h4>Welcome to Live Support!</h4>
                <p>How can we help you today?</p>
              </div>
            ) : (
              <>
                {messages.map((message, index) => {
                  const showDate = index === 0 ||
                    formatDate(messages[index - 1].timestamp) !== formatDate(message.timestamp);

                  return (
                    <React.Fragment key={message.id}>
                      {showDate && (
                        <div className="date-separator">
                          {formatDate(message.timestamp)}
                        </div>
                      )}
                      <div className={`chat-message ${message.sender_id === userId ? 'sent' : 'received'}`}>
                        <div className="message-bubble">
                          {message.sender_id !== userId && message.sender_name && (
                            <div className="sender-name">{message.sender_name}</div>
                          )}
                          <div className="message-text">{message.content}</div>
                          <div className="message-time">{formatTime(message.timestamp)}</div>
                        </div>
                      </div>
                    </React.Fragment>
                  );
                })}
                {typing && (
                  <div className="chat-message received">
                    <div className="message-bubble typing-bubble">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          <form onSubmit={sendMessage} className="chat-input">
            <input
              type="text"
              value={inputMessage}
              onChange={handleInputChange}
              placeholder={isConnected ? "Type a message..." : "Connecting..."}
              disabled={!isConnected}
            />
            <button type="submit" disabled={!isConnected || !inputMessage.trim()}>
              📤
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default LiveChatWidget;
