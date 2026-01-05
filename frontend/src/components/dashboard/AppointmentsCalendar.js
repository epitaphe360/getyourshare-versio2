import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft, ChevronRight, Plus, Calendar, Clock,
  User, MapPin, Video, Phone, Check, X, Bell,
  Filter, Search, MoreVertical, Edit2, Trash2, RefreshCw
} from 'lucide-react';
import './AppointmentsCalendar.css';

const AppointmentsCalendar = ({ userId }) => {
  const [appointments, setAppointments] = useState([]);
  const [currentWeekStart, setCurrentWeekStart] = useState(getWeekStart(new Date()));
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    startTime: '',
    endTime: '',
    type: 'meeting',
    location: '',
    attendee: '',
    reminder: 30,
  });

  // Obtenir le début de la semaine (lundi)
  function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  // Charger les rendez-vous depuis localStorage (simulé)
  useEffect(() => {
    const stored = localStorage.getItem(`appointments_${userId}`);
    if (stored) {
      setAppointments(JSON.parse(stored));
    }
  }, [userId]);

  // Sauvegarder les rendez-vous
  useEffect(() => {
    if (appointments.length > 0) {
      localStorage.setItem(`appointments_${userId}`, JSON.stringify(appointments));
    }
  }, [appointments, userId]);

  // Jours de la semaine
  const weekDays = ['lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.', 'dim.'];

  // Obtenir les dates de la semaine
  const getWeekDates = () => {
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(currentWeekStart);
      date.setDate(currentWeekStart.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  // Filtrer les rendez-vous pour une date
  const getAppointmentsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return appointments.filter(apt => {
      if (apt.date !== dateStr) return false;
      if (selectedFilter === 'all') return true;
      return apt.status === selectedFilter;
    });
  };

  // Navigation semaine
  const goToPreviousWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() - 7);
    setCurrentWeekStart(newStart);
  };

  const goToNextWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() + 7);
    setCurrentWeekStart(newStart);
  };

  const goToToday = () => {
    setCurrentWeekStart(getWeekStart(new Date()));
  };

  // Format de la semaine pour l'affichage
  const formatWeekRange = () => {
    const start = currentWeekStart;
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    
    const startMonth = start.toLocaleDateString('fr-FR', { month: 'long' });
    const endMonth = end.toLocaleDateString('fr-FR', { month: 'long' });
    const year = start.getFullYear();
    
    if (startMonth === endMonth) {
      return `Semaine du ${start.getDate()} ${startMonth} ${year}`;
    }
    return `Semaine du ${start.getDate()} ${startMonth} - ${end.getDate()} ${endMonth} ${year}`;
  };

  // Statistiques
  const stats = {
    confirmed: appointments.filter(a => a.status === 'confirmed').length,
    pending: appointments.filter(a => a.status === 'pending').length,
    cancelled: appointments.filter(a => a.status === 'cancelled').length,
    total: appointments.length
  };

  // Créer un rendez-vous
  const handleCreateAppointment = (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.date || !formData.startTime) {
      return;
    }

    const newAppointment = {
      id: `apt_${Date.now()}`,
      ...formData,
      status: 'pending',
      createdAt: new Date().toISOString(),
    };

    setAppointments([...appointments, newAppointment]);
    setShowCreateModal(false);
    resetForm();
  };

  // Mettre à jour le statut
  const updateStatus = (id, newStatus) => {
    setAppointments(appointments.map(apt => 
      apt.id === id ? { ...apt, status: newStatus } : apt
    ));
  };

  // Supprimer un rendez-vous
  const deleteAppointment = (id) => {
    setAppointments(appointments.filter(apt => apt.id !== id));
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      date: '',
      startTime: '',
      endTime: '',
      type: 'meeting',
      location: '',
      attendee: '',
      reminder: 30,
    });
  };

  // Obtenir l'icône du type
  const getTypeIcon = (type) => {
    switch (type) {
      case 'video': return <Video size={14} />;
      case 'phone': return <Phone size={14} />;
      case 'meeting': return <User size={14} />;
      default: return <Calendar size={14} />;
    }
  };

  // Obtenir la couleur du statut
  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'status-confirmed';
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  };

  const weekDates = getWeekDates();

  return (
    <div className="appointments-calendar">
      {/* Header */}
      <div className="appointments-header">
        <div className="header-left">
          <h2 className="appointments-title">
            <Calendar className="title-icon" size={24} />
            Mes Rendez-vous
          </h2>
          <p className="appointments-subtitle">
            Les rendez-vous que vous avez reçus
          </p>
        </div>
        <div className="header-actions">
          <button className="btn-refresh" onClick={goToToday}>
            <RefreshCw size={18} />
            Aujourd'hui
          </button>
          <button className="btn-create" onClick={() => setShowCreateModal(true)}>
            <Plus size={18} />
            Nouveau RDV
          </button>
        </div>
      </div>

      {/* Filtres */}
      <div className="appointments-filters">
        {[
          { key: 'all', label: 'Tous' },
          { key: 'pending', label: 'En attente' },
          { key: 'confirmed', label: 'Confirmés' },
          { key: 'cancelled', label: 'Annulés' },
        ].map(filter => (
          <button
            key={filter.key}
            className={`filter-btn ${selectedFilter === filter.key ? 'active' : ''}`}
            onClick={() => setSelectedFilter(filter.key)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Navigation semaine */}
      <div className="week-navigation">
        <button className="nav-btn" onClick={goToPreviousWeek}>
          <ChevronLeft size={20} />
          <span>Semaine précédente</span>
        </button>
        <h3 className="week-title">{formatWeekRange()}</h3>
        <button className="nav-btn" onClick={goToNextWeek}>
          <span>Semaine suivante</span>
          <ChevronRight size={20} />
        </button>
      </div>

      {/* Grille semaine */}
      <div className="week-grid">
        {weekDates.map((date, index) => {
          const isToday = date.toDateString() === new Date().toDateString();
          const dayAppointments = getAppointmentsForDate(date);
          
          return (
            <motion.div
              key={index}
              className={`day-column ${isToday ? 'today' : ''}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="day-header">
                <span className="day-name">{weekDays[index]}</span>
                <span className={`day-number ${isToday ? 'today-number' : ''}`}>
                  {date.getDate()}
                </span>
              </div>
              <div className="day-content">
                {dayAppointments.length === 0 ? (
                  <div className="no-appointments">
                    <span>Aucun RDV</span>
                  </div>
                ) : (
                  dayAppointments.map(apt => (
                    <motion.div
                      key={apt.id}
                      className={`appointment-card ${getStatusColor(apt.status)}`}
                      layoutId={apt.id}
                      onClick={() => setSelectedAppointment(apt)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="appointment-time">
                        <Clock size={12} />
                        {apt.startTime}
                      </div>
                      <div className="appointment-title">{apt.title}</div>
                      <div className="appointment-meta">
                        {getTypeIcon(apt.type)}
                        <span>{apt.attendee || 'Client'}</span>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Statistiques */}
      <div className="appointments-stats">
        <div className="stat-card confirmed">
          <Check size={20} />
          <div className="stat-content">
            <span className="stat-label">Confirmés</span>
            <span className="stat-value">{stats.confirmed}</span>
          </div>
        </div>
        <div className="stat-card pending">
          <Clock size={20} />
          <div className="stat-content">
            <span className="stat-label">En attente</span>
            <span className="stat-value">{stats.pending}</span>
          </div>
        </div>
        <div className="stat-card cancelled">
          <X size={20} />
          <div className="stat-content">
            <span className="stat-label">Annulés</span>
            <span className="stat-value">{stats.cancelled}</span>
          </div>
        </div>
        <div className="stat-card total">
          <Calendar size={20} />
          <div className="stat-content">
            <span className="stat-label">Total</span>
            <span className="stat-value">{stats.total}</span>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {appointments.length === 0 && (
        <motion.div 
          className="empty-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="empty-icon">
            <Calendar size={64} />
          </div>
          <h3>Aucun rendez-vous programmé</h3>
          <p>Les visiteurs pourront prendre rendez-vous avec vous via vos créneaux de disponibilité.</p>
          <button className="btn-create-first" onClick={() => setShowCreateModal(true)}>
            <Plus size={18} />
            Créer mon premier rendez-vous
          </button>
        </motion.div>
      )}

      {/* Modal Création */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              className="modal-content"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>
                  <Plus size={20} />
                  Nouveau Rendez-vous
                </h3>
                <button className="close-btn" onClick={() => setShowCreateModal(false)}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleCreateAppointment} className="appointment-form">
                <div className="form-group">
                  <label>Titre du rendez-vous *</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Ex: Réunion de présentation"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Date *</label>
                    <input
                      type="date"
                      value={formData.date}
                      onChange={e => setFormData({ ...formData, date: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Type</label>
                    <select
                      value={formData.type}
                      onChange={e => setFormData({ ...formData, type: e.target.value })}
                    >
                      <option value="meeting">En personne</option>
                      <option value="video">Visioconférence</option>
                      <option value="phone">Appel téléphonique</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Heure de début *</label>
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
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Participant</label>
                  <input
                    type="text"
                    value={formData.attendee}
                    onChange={e => setFormData({ ...formData, attendee: e.target.value })}
                    placeholder="Nom du client ou participant"
                  />
                </div>

                <div className="form-group">
                  <label>Lieu / Lien</label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                    placeholder="Adresse ou lien de réunion"
                  />
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={formData.description}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Notes ou détails supplémentaires..."
                    rows={3}
                  />
                </div>

                <div className="form-group">
                  <label>Rappel</label>
                  <select
                    value={formData.reminder}
                    onChange={e => setFormData({ ...formData, reminder: parseInt(e.target.value) })}
                  >
                    <option value={15}>15 minutes avant</option>
                    <option value={30}>30 minutes avant</option>
                    <option value={60}>1 heure avant</option>
                    <option value={1440}>1 jour avant</option>
                  </select>
                </div>

                <div className="form-actions">
                  <button type="button" className="btn-cancel" onClick={() => setShowCreateModal(false)}>
                    Annuler
                  </button>
                  <button type="submit" className="btn-submit">
                    <Check size={18} />
                    Créer le rendez-vous
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Détail */}
      <AnimatePresence>
        {selectedAppointment && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedAppointment(null)}
          >
            <motion.div
              className="modal-content detail-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>{selectedAppointment.title}</h3>
                <button className="close-btn" onClick={() => setSelectedAppointment(null)}>
                  <X size={20} />
                </button>
              </div>

              <div className="detail-content">
                <div className="detail-row">
                  <Calendar size={18} />
                  <span>{new Date(selectedAppointment.date).toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</span>
                </div>
                <div className="detail-row">
                  <Clock size={18} />
                  <span>{selectedAppointment.startTime} - {selectedAppointment.endTime || '?'}</span>
                </div>
                {selectedAppointment.attendee && (
                  <div className="detail-row">
                    <User size={18} />
                    <span>{selectedAppointment.attendee}</span>
                  </div>
                )}
                {selectedAppointment.location && (
                  <div className="detail-row">
                    <MapPin size={18} />
                    <span>{selectedAppointment.location}</span>
                  </div>
                )}
                {selectedAppointment.description && (
                  <div className="detail-description">
                    <p>{selectedAppointment.description}</p>
                  </div>
                )}

                <div className={`status-badge ${getStatusColor(selectedAppointment.status)}`}>
                  {selectedAppointment.status === 'confirmed' && 'Confirmé'}
                  {selectedAppointment.status === 'pending' && 'En attente'}
                  {selectedAppointment.status === 'cancelled' && 'Annulé'}
                </div>

                <div className="detail-actions">
                  {selectedAppointment.status === 'pending' && (
                    <>
                      <button 
                        className="btn-confirm"
                        onClick={() => {
                          updateStatus(selectedAppointment.id, 'confirmed');
                          setSelectedAppointment(null);
                        }}
                      >
                        <Check size={18} />
                        Confirmer
                      </button>
                      <button 
                        className="btn-cancel-apt"
                        onClick={() => {
                          updateStatus(selectedAppointment.id, 'cancelled');
                          setSelectedAppointment(null);
                        }}
                      >
                        <X size={18} />
                        Annuler
                      </button>
                    </>
                  )}
                  <button 
                    className="btn-delete"
                    onClick={() => {
                      deleteAppointment(selectedAppointment.id);
                      setSelectedAppointment(null);
                    }}
                  >
                    <Trash2 size={18} />
                    Supprimer
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AppointmentsCalendar;
