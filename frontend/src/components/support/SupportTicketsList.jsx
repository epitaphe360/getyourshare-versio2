import React, { useState, useEffect } from 'react';
import { supportAPI } from '../../services/newEndpointsAPI';
import './Support.css';

const SupportTicketsList = ({ onSelectTicket, currentUserId, userRole = 'customer' }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, open, in_progress, closed
  const [priority, setPriority] = useState('all'); // all, low, medium, high, urgent
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  useEffect(() => {
    fetchTickets();
  }, [filter, priority]);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter !== 'all') params.status = filter;
      if (priority !== 'all') params.priority = priority;
      if (userRole === 'customer') params.user_id = currentUserId;

      const response = await supportAPI.getTickets(params);
      setTickets(response.data?.tickets || []);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTicket = (ticket) => {
    setSelectedTicketId(ticket.id);
    onSelectTicket(ticket);
  };

  const getPriorityColor = (priorityLevel) => {
    const colors = {
      low: '#4caf50',
      medium: '#ff9800',
      high: '#f44336',
      urgent: '#9c27b0',
    };
    return colors[priorityLevel] || '#666';
  };

  const getStatusColor = (status) => {
    const colors = {
      open: '#2196f3',
      in_progress: '#ff9800',
      resolved: '#4caf50',
      closed: '#9e9e9e',
    };
    return colors[status] || '#666';
  };

  const getPriorityIcon = (priorityLevel) => {
    const icons = {
      low: '🟢',
      medium: '🟡',
      high: '🔴',
      urgent: '🚨',
    };
    return icons[priorityLevel] || '⚪';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
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

  const filteredTickets = tickets.filter(ticket => {
    if (!searchQuery) return true;
    return (
      ticket.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.ticket_number?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  if (loading) {
    return (
      <div className="support-tickets-list">
        <div className="tickets-header">
          <h3>Support Tickets</h3>
        </div>
        <div className="loading-state">Loading tickets...</div>
      </div>
    );
  }

  return (
    <div className="support-tickets-list">
      <div className="tickets-header">
        <h3>Support Tickets</h3>
        <button onClick={fetchTickets} className="refresh-btn-small">
          🔄
        </button>
      </div>

      <div className="tickets-filters">
        <div className="filter-section">
          <label>Status</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>

        <div className="filter-section">
          <label>Priority</label>
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div className="filter-section search-section">
          <label>Search</label>
          <input
            type="text"
            className="search-input"
            placeholder="Search tickets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="tickets-stats">
        <div className="stat-item">
          <span className="stat-number">{tickets.length}</span>
          <span className="stat-label">Total</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tickets.filter(t => t.status === 'open').length}</span>
          <span className="stat-label">Open</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tickets.filter(t => t.status === 'in_progress').length}</span>
          <span className="stat-label">In Progress</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{tickets.filter(t => t.status === 'resolved').length}</span>
          <span className="stat-label">Resolved</span>
        </div>
      </div>

      <div className="tickets-container">
        {filteredTickets.length === 0 ? (
          <div className="empty-tickets">
            <div className="empty-icon">🎫</div>
            <p>No tickets found</p>
          </div>
        ) : (
          filteredTickets.map(ticket => (
            <div
              key={ticket.id}
              className={`ticket-item ${selectedTicketId === ticket.id ? 'selected' : ''}`}
              onClick={() => handleSelectTicket(ticket)}
            >
              <div className="ticket-header-row">
                <div className="ticket-number">
                  {getPriorityIcon(ticket.priority)} #{ticket.ticket_number}
                </div>
                <div className="ticket-date">{formatDate(ticket.created_at)}</div>
              </div>

              <div className="ticket-subject">{ticket.subject}</div>

              <div className="ticket-description">
                {ticket.description && ticket.description.length > 100
                  ? `${ticket.description.substring(0, 100)}...`
                  : ticket.description}
              </div>

              <div className="ticket-footer">
                <div className="ticket-badges">
                  <span
                    className="status-badge"
                    style={{ background: getStatusColor(ticket.status), color: 'white' }}
                  >
                    {ticket.status.replace('_', ' ')}
                  </span>
                  <span
                    className="priority-badge"
                    style={{ background: getPriorityColor(ticket.priority), color: 'white' }}
                  >
                    {ticket.priority}
                  </span>
                  {ticket.category && (
                    <span className="category-badge">
                      {ticket.category}
                    </span>
                  )}
                </div>

                {ticket.assigned_to && (
                  <div className="assigned-info">
                    Assigned to: {ticket.assigned_to.name || 'Support Team'}
                  </div>
                )}

                {ticket.replies_count > 0 && (
                  <div className="replies-count">
                    💬 {ticket.replies_count} {ticket.replies_count === 1 ? 'reply' : 'replies'}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SupportTicketsList;
