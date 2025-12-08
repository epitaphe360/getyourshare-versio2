import React, { useState, useEffect, useRef } from 'react';
import { liveChatAPI } from '../../services/newEndpointsAPI';
import './LiveChat.css';

const ChatWindow = ({ room, currentUserId, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [attachmentFile, setAttachmentFile] = useState(null);

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  useEffect(() => {
    if (room) {
      loadChatHistory();
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [room]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async () => {
    setLoading(true);
    try {
      const response = await liveChatAPI.getRoomHistory(room.id);
      setMessages(response.data?.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    const wsURL = liveChatAPI.getWebSocketURL(currentUserId);
    const ws = new WebSocket(wsURL);

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'join_room',
        room_id: room.id,
        user_id: currentUserId,
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'message' && data.room_id === room.id) {
        setMessages(prev => [...prev, {
          id: data.message_id || Date.now(),
          content: data.content,
          sender_id: data.sender_id,
          sender_name: data.sender_name,
          timestamp: data.timestamp,
          attachments: data.attachments,
        }]);
      } else if (data.type === 'typing' && data.sender_id !== currentUserId) {
        setIsTyping(true);
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }
        typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 3000);
      }
    };

    wsRef.current = ws;
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if ((!inputMessage.trim() && !attachmentFile) || sending) return;

    setSending(true);

    try {
      const messageData = {
        room_id: room.id,
        content: inputMessage,
      };

      if (attachmentFile) {
        // In a real implementation, upload the file first
        messageData.attachments = [{
          name: attachmentFile.name,
          size: attachmentFile.size,
          type: attachmentFile.type,
        }];
      }

      await liveChatAPI.sendMessage(messageData);

      // Also send via WebSocket for real-time delivery
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'message',
          room_id: room.id,
          content: inputMessage,
          sender_id: currentUserId,
          timestamp: new Date().toISOString(),
        }));
      }

      setInputMessage('');
      setAttachmentFile(null);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const sendTypingIndicator = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        room_id: room.id,
        sender_id: currentUserId,
      }));
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }
      setAttachmentFile(file);
    }
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
      return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    }
  };

  const getParticipantName = () => {
    if (!room.participants) return 'Unknown User';
    const otherParticipant = room.participants.find(p => p.id !== currentUserId);
    return otherParticipant?.name || 'Unknown User';
  };

  if (!room) {
    return (
      <div className="chat-window">
        <div className="no-room-selected">
          <div className="no-room-icon">💬</div>
          <h3>No chat selected</h3>
          <p>Select a chat room from the list to start messaging</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-window-header">
        <div className="header-user-info">
          <div className="user-avatar">
            {room.avatar_url ? (
              <img src={room.avatar_url} alt={getParticipantName()} />
            ) : (
              <div className="avatar-placeholder">
                {getParticipantName().charAt(0).toUpperCase()}
              </div>
            )}
            {room.is_online && <span className="online-indicator-large"></span>}
          </div>
          <div className="user-details">
            <h3>{getParticipantName()}</h3>
            <span className="user-status">
              {room.is_online ? '🟢 Online' : '⚫ Offline'}
            </span>
          </div>
        </div>
        <div className="header-actions">
          <button onClick={loadChatHistory} className="icon-btn" title="Refresh">
            🔄
          </button>
          {onClose && (
            <button onClick={onClose} className="icon-btn" title="Close">
              ✖
            </button>
          )}
        </div>
      </div>

      <div className="chat-window-messages">
        {loading ? (
          <div className="loading-messages">Loading messages...</div>
        ) : messages.length === 0 ? (
          <div className="no-messages">
            <div className="no-messages-icon">💬</div>
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => {
              const showDate = index === 0 ||
                formatDate(messages[index - 1].timestamp) !== formatDate(message.timestamp);

              return (
                <React.Fragment key={message.id}>
                  {showDate && (
                    <div className="date-divider">
                      {formatDate(message.timestamp)}
                    </div>
                  )}
                  <div className={`message-row ${message.sender_id === currentUserId ? 'sent' : 'received'}`}>
                    {message.sender_id !== currentUserId && (
                      <div className="message-avatar-small">
                        {message.sender_name?.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div className="message-content-wrapper">
                      {message.sender_id !== currentUserId && (
                        <div className="message-sender-name">{message.sender_name}</div>
                      )}
                      <div className="message-bubble-advanced">
                        <div className="message-text">{message.content}</div>
                        {message.attachments && message.attachments.length > 0 && (
                          <div className="message-attachments">
                            {message.attachments.map((attachment, idx) => (
                              <div key={idx} className="attachment-item">
                                📎 {attachment.name}
                              </div>
                            ))}
                          </div>
                        )}
                        <div className="message-timestamp">{formatTime(message.timestamp)}</div>
                      </div>
                    </div>
                  </div>
                </React.Fragment>
              );
            })}
            {isTyping && (
              <div className="message-row received">
                <div className="message-avatar-small">
                  {getParticipantName().charAt(0).toUpperCase()}
                </div>
                <div className="message-content-wrapper">
                  <div className="message-bubble-advanced typing-bubble">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <form onSubmit={sendMessage} className="chat-window-input">
        {attachmentFile && (
          <div className="attachment-preview">
            <span>📎 {attachmentFile.name}</span>
            <button
              type="button"
              onClick={() => setAttachmentFile(null)}
              className="remove-attachment"
            >
              ✖
            </button>
          </div>
        )}
        <div className="input-row">
          <label className="attach-btn" title="Attach file">
            📎
            <input
              type="file"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept="image/*,.pdf,.doc,.docx"
            />
          </label>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => {
              setInputMessage(e.target.value);
              sendTypingIndicator();
            }}
            placeholder="Type your message..."
            disabled={sending}
          />
          <button type="submit" disabled={sending || (!inputMessage.trim() && !attachmentFile)}>
            {sending ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatWindow;
