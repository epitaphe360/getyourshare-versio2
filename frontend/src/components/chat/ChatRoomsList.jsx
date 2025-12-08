import React, { useState, useEffect } from 'react';
import { liveChatAPI } from '../../services/newEndpointsAPI';
import './LiveChat.css';

const ChatRoomsList = ({ onSelectRoom, currentUserId, userRole = 'support' }) => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, active, archived
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRoomId, setSelectedRoomId] = useState(null);

  useEffect(() => {
    fetchRooms();
    // Poll for updates every 10 seconds
    const interval = setInterval(fetchRooms, 10000);
    return () => clearInterval(interval);
  }, [filter]);

  const fetchRooms = async () => {
    try {
      const response = await liveChatAPI.getRooms();
      let roomsList = response.data?.rooms || [];

      // Apply filter
      if (filter === 'active') {
        roomsList = roomsList.filter(room => room.status === 'active');
      } else if (filter === 'archived') {
        roomsList = roomsList.filter(room => room.status === 'archived');
      }

      // Sort by last message time (most recent first)
      roomsList.sort((a, b) => {
        const timeA = new Date(a.last_message_at || a.created_at);
        const timeB = new Date(b.last_message_at || b.created_at);
        return timeB - timeA;
      });

      setRooms(roomsList);
    } catch (error) {
      console.error('Error fetching rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRoom = (room) => {
    setSelectedRoomId(room.id);
    onSelectRoom(room);
  };

  const handleArchiveRoom = async (roomId, e) => {
    e.stopPropagation();
    try {
      await liveChatAPI.archiveRoom(roomId);
      fetchRooms();
    } catch (error) {
      console.error('Error archiving room:', error);
    }
  };

  const handleDeleteRoom = async (roomId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this chat room?')) return;

    try {
      await liveChatAPI.deleteRoom(roomId);
      fetchRooms();
    } catch (error) {
      console.error('Error deleting room:', error);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getParticipantName = (room) => {
    if (!room.participants || room.participants.length === 0) return 'Unknown User';

    // Find participant that's not the current user
    const otherParticipant = room.participants.find(p => p.id !== currentUserId);
    return otherParticipant?.name || room.participants[0]?.name || 'Unknown User';
  };

  const filteredRooms = rooms.filter(room => {
    if (!searchQuery) return true;
    const participantName = getParticipantName(room).toLowerCase();
    const lastMessage = room.last_message?.toLowerCase() || '';
    return participantName.includes(searchQuery.toLowerCase()) ||
           lastMessage.includes(searchQuery.toLowerCase());
  });

  if (loading) {
    return (
      <div className="chat-rooms-list">
        <div className="rooms-header">
          <h3>Chat Rooms</h3>
        </div>
        <div className="loading-state">Loading chat rooms...</div>
      </div>
    );
  }

  return (
    <div className="chat-rooms-list">
      <div className="rooms-header">
        <h3>Chat Rooms</h3>
        <button onClick={fetchRooms} className="refresh-btn-small">
          🔄
        </button>
      </div>

      <div className="rooms-filters">
        <div className="filter-tabs">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All ({rooms.length})
          </button>
          <button
            className={filter === 'active' ? 'active' : ''}
            onClick={() => setFilter('active')}
          >
            Active
          </button>
          <button
            className={filter === 'archived' ? 'active' : ''}
            onClick={() => setFilter('archived')}
          >
            Archived
          </button>
        </div>

        <input
          type="text"
          className="search-input"
          placeholder="Search rooms..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="rooms-container">
        {filteredRooms.length === 0 ? (
          <div className="empty-rooms">
            <div className="empty-icon">💬</div>
            <p>No chat rooms {filter !== 'all' ? filter : 'available'}</p>
          </div>
        ) : (
          filteredRooms.map(room => (
            <div
              key={room.id}
              className={`room-item ${selectedRoomId === room.id ? 'selected' : ''} ${room.unread_count > 0 ? 'has-unread' : ''}`}
              onClick={() => handleSelectRoom(room)}
            >
              <div className="room-avatar">
                {room.avatar_url ? (
                  <img src={room.avatar_url} alt={getParticipantName(room)} />
                ) : (
                  <div className="avatar-placeholder">
                    {getParticipantName(room).charAt(0).toUpperCase()}
                  </div>
                )}
                {room.is_online && <span className="online-indicator"></span>}
              </div>

              <div className="room-info">
                <div className="room-header-row">
                  <span className="room-name">{getParticipantName(room)}</span>
                  <span className="room-time">{formatTime(room.last_message_at || room.created_at)}</span>
                </div>

                <div className="room-last-message">
                  {room.last_message ? (
                    <span className={room.unread_count > 0 ? 'unread' : ''}>
                      {room.last_message.length > 50
                        ? `${room.last_message.substring(0, 50)}...`
                        : room.last_message}
                    </span>
                  ) : (
                    <span className="no-messages">No messages yet</span>
                  )}
                  {room.unread_count > 0 && (
                    <span className="unread-count-badge">{room.unread_count}</span>
                  )}
                </div>

                {room.tags && room.tags.length > 0 && (
                  <div className="room-tags">
                    {room.tags.slice(0, 2).map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>

              {userRole === 'support' || userRole === 'admin' ? (
                <div className="room-actions" onClick={(e) => e.stopPropagation()}>
                  {room.status === 'active' && (
                    <button
                      onClick={(e) => handleArchiveRoom(room.id, e)}
                      className="action-btn-small archive-btn"
                      title="Archive"
                    >
                      📥
                    </button>
                  )}
                  <button
                    onClick={(e) => handleDeleteRoom(room.id, e)}
                    className="action-btn-small delete-btn"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              ) : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatRoomsList;
