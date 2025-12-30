import React, { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, Trash2, Edit2, Link2 } from 'lucide-react';

// Custom Google Icon component (GoogleIcon n'existe pas dans lucide-react)
const GoogleIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);
import { motion, AnimatePresence } from 'framer-motion';
import './CalendarIntegration.css';

const CalendarIntegration = ({ userId }) => {
  const [events, setEvents] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [showEventForm, setShowEventForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [googleSyncStatus, setGoogleSyncStatus] = useState('disconnected');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    startTime: '',
    endTime: '',
    type: 'meeting', // meeting, call, task, reminder
    reminder: 15, // minutes
  });

  // Load events from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(`calendar_events_${userId}`);
    if (stored) {
      setEvents(JSON.parse(stored));
    }
    
    // Load Google sync status
    const googleStatus = localStorage.getItem(`google_sync_${userId}`);
    if (googleStatus) {
      setGoogleSyncStatus(googleStatus);
    }
  }, [userId]);

  // Save events to localStorage
  useEffect(() => {
    localStorage.setItem(`calendar_events_${userId}`, JSON.stringify(events));
  }, [events, userId]);

  // Get days in month
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  // Get first day of month
  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  // Format date for display
  const formatDate = (date) => {
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Get events for specific date
  const getEventsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(event => event.date === dateStr);
  };

  // Handle previous month
  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  // Handle next month
  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  // Handle date click
  const handleDateClick = (day) => {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    setSelectedDate(date);
    setShowEventForm(true);
    setEditingEvent(null);
    setFormData({
      title: '',
      description: '',
      startTime: '',
      endTime: '',
      type: 'meeting',
      reminder: 15,
    });
  };

  // Handle form submit
  const handleSubmitEvent = (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.startTime || !formData.endTime) {
      alert('Veuillez remplir tous les champs');
      return;
    }

    if (!selectedDate) return;

    const dateStr = selectedDate.toISOString().split('T')[0];

    if (editingEvent) {
      setEvents(events.map(evt =>
        evt.id === editingEvent.id
          ? {
              ...evt,
              ...formData,
              date: dateStr,
              updatedAt: new Date().toISOString(),
            }
          : evt
      ));
    } else {
      const newEvent = {
        id: `event_${Date.now()}`,
        ...formData,
        date: dateStr,
        createdAt: new Date().toISOString(),
      };
      setEvents([...events, newEvent]);
    }

    setShowEventForm(false);
    setEditingEvent(null);
  };

  // Handle event delete
  const handleDeleteEvent = (eventId) => {
    setEvents(events.filter(evt => evt.id !== eventId));
  };

  // Handle Google Sync
  const handleGoogleSync = async () => {
    if (googleSyncStatus === 'disconnected') {
      // Simulated Google OAuth flow
      const clientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
      const redirectUri = `${window.location.origin}/oauth/google-calendar`;
      const scope = 'https://www.googleapis.com/auth/calendar';
      
      const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
      
      // For now, simulate connection
      localStorage.setItem(`google_sync_${userId}`, 'connected');
      setGoogleSyncStatus('connected');
      
      // Simulate syncing some events
      setTimeout(() => {
        setGoogleSyncStatus('synced');
      }, 2000);
    } else {
      localStorage.removeItem(`google_sync_${userId}`);
      setGoogleSyncStatus('disconnected');
    }
  };

  // Export to iCal
  const handleExportICal = () => {
    const icalContent = generateICal(events);
    const blob = new Blob([icalContent], { type: 'text/calendar' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `calendar_${new Date().toISOString().split('T')[0]}.ics`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Generate iCal format
  const generateICal = (eventsList) => {
    const now = new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    let ical = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//GetYourShare//Commercial Calendar//FR
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Commercial Calendar
X-WR-TIMEZONE:Europe/Paris
BEGIN:VTIMEZONE
TZID:Europe/Paris
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE\n`;

    eventsList.forEach(event => {
      const [startDate, startTime] = [event.date, event.startTime];
      const [endDate, endTime] = [event.date, event.endTime];
      
      const dtStart = `${startDate.replace(/-/g, '')}T${startTime.replace(/:/g, '')}00`;
      const dtEnd = `${endDate.replace(/-/g, '')}T${endTime.replace(/:/g, '')}00`;

      ical += `BEGIN:VEVENT
UID:${event.id}@getyourshare.com
DTSTAMP:${now}
DTSTART;TZID=Europe/Paris:${dtStart}
DTEND;TZID=Europe/Paris:${dtEnd}
SUMMARY:${event.title}
DESCRIPTION:${event.description || 'Sans description'}
CATEGORIES:${event.type.toUpperCase()}
TRANSP:OPAQUE
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT\n`;
    });

    ical += 'END:VCALENDAR';
    return ical;
  };

  // Render calendar grid
  const renderCalendarDays = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];

    // Empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-empty"></div>);
    }

    // Days of month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const isToday = date.toDateString() === new Date().toDateString();
      const isSelected = selectedDate?.toDateString() === date.toDateString();
      const dayEvents = getEventsForDate(date);
      const hasEvents = dayEvents.length > 0;

      days.push(
        <motion.div
          key={day}
          className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${hasEvents ? 'has-events' : ''}`}
          onClick={() => handleDateClick(day)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <div className="day-number">{day}</div>
          <div className="day-events">
            {dayEvents.slice(0, 2).map(evt => (
              <div key={evt.id} className={`event-dot ${evt.type}`}></div>
            ))}
            {dayEvents.length > 2 && <span className="more-events">+{dayEvents.length - 2}</span>}
          </div>
        </motion.div>
      );
    }

    return days;
  };

  return (
    <motion.div
      className="calendar-integration"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="calendar-header">
        <h2>📅 Calendrier Commercial</h2>
        <div className="calendar-actions">
          <button
            className={`google-sync-btn ${googleSyncStatus}`}
            onClick={handleGoogleSync}
            title="Synchroniser avec Google Calendar"
          >
            <GoogleIcon size={18} />
            {googleSyncStatus === 'connected' ? 'Synchronisé' : 'Connexion Google'}
          </button>
          <button
            className="export-ical-btn"
            onClick={handleExportICal}
            title="Exporter en iCal"
          >
            <CalendarIcon size={18} />
            Exporter iCal
          </button>
        </div>
      </div>

      <div className="calendar-container">
        <div className="calendar-main">
          <div className="calendar-navigation">
            <button onClick={handlePrevMonth} className="nav-btn">
              <ChevronLeft size={20} />
            </button>
            <h3 className="current-month">
              {currentDate.toLocaleDateString('fr-FR', {
                month: 'long',
                year: 'numeric',
              })}
            </h3>
            <button onClick={handleNextMonth} className="nav-btn">
              <ChevronRight size={20} />
            </button>
          </div>

          <div className="calendar-weekdays">
            {['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'].map(day => (
              <div key={day} className="weekday">
                {day}
              </div>
            ))}
          </div>

          <div className="calendar-grid">
            {renderCalendarDays()}
          </div>
        </div>

        <div className="calendar-sidebar">
          <div className="selected-date-info">
            {selectedDate && (
              <>
                <h4>{formatDate(selectedDate)}</h4>
                <button
                  className="add-event-btn"
                  onClick={() => setShowEventForm(true)}
                >
                  <Plus size={18} />
                  Ajouter événement
                </button>
              </>
            )}
          </div>

          <div className="events-list">
            <h4>Événements à venir</h4>
            {events
              .filter(evt => new Date(evt.date) >= new Date(new Date().toISOString().split('T')[0]))
              .sort((a, b) => new Date(a.date + 'T' + a.startTime) - new Date(b.date + 'T' + b.startTime))
              .slice(0, 10)
              .map(evt => (
                <motion.div
                  key={evt.id}
                  className={`event-item ${evt.type}`}
                  layout
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="event-content">
                    <div className="event-type-badge">{evt.type}</div>
                    <div>
                      <p className="event-title">{evt.title}</p>
                      <p className="event-time">{evt.date} à {evt.startTime}</p>
                    </div>
                  </div>
                  <div className="event-actions">
                    <button
                      className="edit-btn"
                      onClick={() => {
                        setEditingEvent(evt);
                        setSelectedDate(new Date(evt.date));
                        setFormData({
                          title: evt.title,
                          description: evt.description,
                          startTime: evt.startTime,
                          endTime: evt.endTime,
                          type: evt.type,
                          reminder: evt.reminder,
                        });
                        setShowEventForm(true);
                      }}
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDeleteEvent(evt.id)}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </motion.div>
              ))}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {showEventForm && (
          <motion.div
            className="event-form-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowEventForm(false)}
          >
            <motion.form
              className="event-form"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              onSubmit={handleSubmitEvent}
            >
              <h3>{editingEvent ? 'Modifier événement' : 'Nouvel événement'}</h3>

              <input
                type="text"
                placeholder="Titre de l'événement"
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                required
              />

              <textarea
                placeholder="Description (optionnel)"
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                rows="3"
              ></textarea>

              <div className="form-row">
                <div className="form-group">
                  <label>Heure de début</label>
                  <input
                    type="time"
                    value={formData.startTime}
                    onChange={e => setFormData({ ...formData, startTime: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Heure de fin</label>
                  <input
                    type="time"
                    value={formData.endTime}
                    onChange={e => setFormData({ ...formData, endTime: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Type d'événement</label>
                  <select
                    value={formData.type}
                    onChange={e => setFormData({ ...formData, type: e.target.value })}
                  >
                    <option value="meeting">Réunion</option>
                    <option value="call">Appel</option>
                    <option value="task">Tâche</option>
                    <option value="reminder">Rappel</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Rappel (minutes avant)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.reminder}
                    onChange={e => setFormData({ ...formData, reminder: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowEventForm(false)}
                >
                  Annuler
                </button>
                <button type="submit" className="submit-btn">
                  {editingEvent ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </motion.form>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default CalendarIntegration;
