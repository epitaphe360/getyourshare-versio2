import React, { useState } from 'react';
import { supportAPI } from '../../services/newEndpointsAPI';
import './Support.css';

const CreateTicketForm = ({ onTicketCreated, onCancel }) => {
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    category: 'general',
    priority: 'medium',
  });
  const [attachments, setAttachments] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const categories = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'technical', label: 'Technical Support' },
    { value: 'billing', label: 'Billing' },
    { value: 'account', label: 'Account Issues' },
    { value: 'feature_request', label: 'Feature Request' },
    { value: 'bug_report', label: 'Bug Report' },
    { value: 'other', label: 'Other' },
  ];

  const priorities = [
    { value: 'low', label: 'Low - General question' },
    { value: 'medium', label: 'Medium - Needs attention' },
    { value: 'high', label: 'High - Urgent issue' },
    { value: 'urgent', label: 'Urgent - Critical problem' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.subject.trim()) {
      setError('Subject is required');
      return;
    }

    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }

    setSubmitting(true);

    try {
      const ticketData = {
        ...formData,
        attachments: attachments.map(file => ({
          name: file.name,
          size: file.size,
          type: file.type,
        })),
      };

      const response = await supportAPI.createTicket(ticketData);

      // Upload attachments if any
      if (attachments.length > 0 && response.data?.ticket_id) {
        // In a real implementation, upload files here
        console.log('Would upload attachments for ticket:', response.data.ticket_id);
      }

      alert('Support ticket created successfully!');

      // Reset form
      setFormData({
        subject: '',
        description: '',
        category: 'general',
        priority: 'medium',
      });
      setAttachments([]);

      if (onTicketCreated) {
        onTicketCreated(response.data);
      }
    } catch (err) {
      console.error('Error creating ticket:', err);
      setError(err.response?.data?.message || 'Failed to create ticket. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);

    // Check file sizes (max 5MB each)
    const invalidFiles = files.filter(file => file.size > 5 * 1024 * 1024);
    if (invalidFiles.length > 0) {
      setError('Each file must be less than 5MB');
      return;
    }

    // Max 5 files
    if (attachments.length + files.length > 5) {
      setError('Maximum 5 attachments allowed');
      return;
    }

    setAttachments([...attachments, ...files]);
    setError(null);
  };

  const removeAttachment = (index) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="create-ticket-form">
      <div className="form-header">
        <h3>Create New Support Ticket</h3>
        {onCancel && (
          <button onClick={onCancel} className="close-form-btn">
            ✖
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="subject">Subject *</label>
          <input
            id="subject"
            type="text"
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            placeholder="Brief description of your issue"
            required
            maxLength={200}
          />
          <small>{formData.subject.length}/200 characters</small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              required
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="priority">Priority *</label>
            <select
              id="priority"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              required
            >
              {priorities.map(pri => (
                <option key={pri.value} value={pri.value}>
                  {pri.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Please provide as much detail as possible..."
            required
            rows="6"
            maxLength={2000}
          />
          <small>{formData.description.length}/2000 characters</small>
        </div>

        <div className="form-group">
          <label>Attachments (Optional)</label>
          <div className="file-upload-area">
            <label htmlFor="file-upload" className="file-upload-label">
              📎 Attach files (Max 5 files, 5MB each)
              <input
                id="file-upload"
                type="file"
                onChange={handleFileSelect}
                multiple
                accept="image/*,.pdf,.doc,.docx,.txt"
                style={{ display: 'none' }}
              />
            </label>
          </div>

          {attachments.length > 0 && (
            <div className="attachments-list">
              {attachments.map((file, index) => (
                <div key={index} className="attachment-preview">
                  <span className="file-icon">
                    {file.type.startsWith('image/') ? '🖼️' : '📄'}
                  </span>
                  <div className="file-info">
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{formatFileSize(file.size)}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeAttachment(index)}
                    className="remove-file-btn"
                  >
                    ✖
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-info-box">
          <strong>💡 Tips for faster resolution:</strong>
          <ul>
            <li>Be specific about the issue you're experiencing</li>
            <li>Include steps to reproduce the problem</li>
            <li>Attach screenshots or relevant files if applicable</li>
            <li>Mention any error messages you received</li>
          </ul>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={submitting}
          >
            {submitting ? '⏳ Creating...' : '📤 Create Ticket'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="cancel-btn"
              disabled={submitting}
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default CreateTicketForm;
