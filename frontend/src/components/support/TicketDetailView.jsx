import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import { supportAPI } from '../../services/newEndpointsAPI';
import './Support.css';

const TicketDetailView = ({ ticket, currentUserId, userRole = 'customer', onClose, onUpdate }) => {
  const [ticketData, setTicketData] = useState(ticket);
  const [replies, setReplies] = useState([]);
  const [replyMessage, setReplyMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [updating, setUpdating] = useState(false);

  const repliesEndRef = useRef(null);

  useEffect(() => {
    if (ticket) {
      fetchTicketDetails();
      scrollToBottom();
    }
  }, [ticket]);

  const fetchTicketDetails = async () => {
    setLoading(true);
    try {
      const response = await supportAPI.getTicket(ticket.id);
      setTicketData(response.data?.ticket || ticket);
      setReplies(response.data?.replies || []);
    } catch (error) {
      console.error('Error fetching ticket details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!replyMessage.trim() || sending) return;

    setSending(true);
    try {
      await supportAPI.replyToTicket(ticket.id, { message: replyMessage });

      // Refresh ticket details to get new replies
      await fetchTicketDetails();

      setReplyMessage('');
      toast.success('Réponse envoyée avec succès !');
      scrollToBottom();
    } catch (error) {
      console.error('Error sending reply:', error);
      toast.error('Erreur lors de l’envoi de la réponse. Veuillez réessayer.');
    } finally {
      setSending(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    setUpdating(true);
    try {
      await supportAPI.updateTicketStatus(ticket.id, newStatus);
      setTicketData({ ...ticketData, status: newStatus });

      if (onUpdate) {
        onUpdate({ ...ticketData, status: newStatus });
      }

      toast.success(`Statut du ticket mis à jour : ${newStatus}`);
    } catch (error) {
      console.error('Error updating ticket status:', error);
      toast.error('Erreur lors de la mise à jour du statut.');
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdatePriority = async (newPriority) => {
    setUpdating(true);
    try {
      await supportAPI.updateTicketPriority(ticket.id, newPriority);
      setTicketData({ ...ticketData, priority: newPriority });

      if (onUpdate) {
        onUpdate({ ...ticketData, priority: newPriority });
      }

      toast.success(`Priorité du ticket mise à jour : ${newPriority}`);
    } catch (error) {
      console.error('Error updating ticket priority:', error);
      toast.error('Erreur lors de la mise à jour de la priorité.');
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignTicket = async (agentId) => {
    setUpdating(true);
    try {
      await supportAPI.assignTicket(ticket.id, agentId);
      toast.success('Ticket assigné avec succès !');
      await fetchTicketDetails();
    } catch (error) {
      console.error('Error assigning ticket:', error);
      toast.error('Erreur lors de l’assignation du ticket.');
    } finally {
      setUpdating(false);
    }
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      repliesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: '#4caf50',
      medium: '#ff9800',
      high: '#f44336',
      urgent: '#9c27b0',
    };
    return colors[priority] || '#666';
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

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!ticketData) {
    return (
      <div className="ticket-detail-view">
        <div className="no-ticket-selected">
          <div className="no-ticket-icon">🎫</div>
          <h3>No Ticket Selected</h3>
          <p>Select a ticket from the list to view details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ticket-detail-view">
      <div className="ticket-detail-header">
        <div className="header-title">
          <h3>Ticket #{ticketData.ticket_number}</h3>
          <div className="ticket-meta">
            Created {formatDateTime(ticketData.created_at)}
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="close-detail-btn">
            ✖
          </button>
        )}
      </div>

      <div className="ticket-detail-content">
        {/* Ticket Info Section */}
        <div className="ticket-info-section">
          <div className="info-row">
            <div className="info-item">
              <span className="info-label">Status</span>
              {userRole === 'support' || userRole === 'admin' ? (
                <select
                  value={ticketData.status}
                  onChange={(e) => handleUpdateStatus(e.target.value)}
                  className="status-select"
                  disabled={updating}
                  style={{ color: getStatusColor(ticketData.status) }}
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              ) : (
                <span
                  className="status-badge"
                  style={{ background: getStatusColor(ticketData.status), color: 'white' }}
                >
                  {ticketData.status.replace('_', ' ')}
                </span>
              )}
            </div>

            <div className="info-item">
              <span className="info-label">Priority</span>
              {userRole === 'support' || userRole === 'admin' ? (
                <select
                  value={ticketData.priority}
                  onChange={(e) => handleUpdatePriority(e.target.value)}
                  className="priority-select"
                  disabled={updating}
                  style={{ color: getPriorityColor(ticketData.priority) }}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              ) : (
                <span
                  className="priority-badge"
                  style={{ background: getPriorityColor(ticketData.priority), color: 'white' }}
                >
                  {ticketData.priority}
                </span>
              )}
            </div>

            <div className="info-item">
              <span className="info-label">Category</span>
              <span className="info-value">{ticketData.category}</span>
            </div>
          </div>

          {ticketData.assigned_to && (
            <div className="assigned-section">
              <strong>Assigned to:</strong> {ticketData.assigned_to.name || 'Support Team'}
            </div>
          )}
        </div>

        {/* Subject and Description */}
        <div className="ticket-main-content">
          <h4 className="ticket-subject">{ticketData.subject}</h4>
          <div className="ticket-description">
            {ticketData.description}
          </div>

          {ticketData.attachments && ticketData.attachments.length > 0 && (
            <div className="ticket-attachments">
              <strong>Attachments:</strong>
              <div className="attachments-grid">
                {ticketData.attachments.map((attachment, index) => (
                  <a
                    key={index}
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="attachment-link"
                  >
                    📎 {attachment.name}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Replies Section */}
        <div className="ticket-replies-section">
          <h4>Conversation ({replies.length})</h4>

          {loading ? (
            <div className="loading-replies">Loading replies...</div>
          ) : replies.length === 0 ? (
            <div className="no-replies">No replies yet. Be the first to respond!</div>
          ) : (
            <div className="replies-list">
              {replies.map((reply) => (
                <div
                  key={reply.id}
                  className={`reply-item ${reply.user_id === currentUserId ? 'own-reply' : 'other-reply'}`}
                >
                  <div className="reply-header">
                    <div className="reply-author">
                      <div className="author-avatar">
                        {reply.author_name?.charAt(0).toUpperCase() || '?'}
                      </div>
                      <div>
                        <div className="author-name">
                          {reply.author_name || 'Unknown User'}
                          {reply.author_role && (
                            <span className="author-role">({reply.author_role})</span>
                          )}
                        </div>
                        <div className="reply-time">{formatDateTime(reply.created_at)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="reply-message">{reply.message}</div>
                </div>
              ))}
              <div ref={repliesEndRef} />
            </div>
          )}
        </div>

        {/* Reply Input */}
        {ticketData.status !== 'closed' && (
          <form onSubmit={handleSendReply} className="reply-form">
            <textarea
              value={replyMessage}
              onChange={(e) => setReplyMessage(e.target.value)}
              placeholder="Type your reply..."
              rows="4"
              disabled={sending}
            />
            <div className="reply-actions">
              <button
                type="submit"
                className="send-reply-btn"
                disabled={sending || !replyMessage.trim()}
              >
                {sending ? '⏳ Sending...' : '📤 Send Reply'}
              </button>
            </div>
          </form>
        )}

        {ticketData.status === 'closed' && (
          <div className="ticket-closed-notice">
            This ticket is closed. Reopen it to continue the conversation.
          </div>
        )}
      </div>
    </div>
  );
};

export default TicketDetailView;
