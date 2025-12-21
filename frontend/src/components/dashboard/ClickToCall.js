import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Mic, MicOff, Volume2, VolumeX, Clock, SkipBack, SkipForward } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './ClickToCall.css';

const ClickToCall = ({ userId, leads = [] }) => {
  const [isCallActive, setIsCallActive] = useState(false);
  const [currentCall, setCurrentCall] = useState(null);
  const [callHistory, setCallHistory] = useState([]);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [callRecording, setCallRecording] = useState(false);
  const [callTranscript, setCallTranscript] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [showLeadSelector, setShowLeadSelector] = useState(false);
  const timerRef = useRef(null);
  const recordingRef = useRef(null);

  // Load call history from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(`call_history_${userId}`);
    if (stored) {
      setCallHistory(JSON.parse(stored));
    }
  }, [userId]);

  // Save call history to localStorage
  useEffect(() => {
    localStorage.setItem(`call_history_${userId}`, JSON.stringify(callHistory));
  }, [callHistory, userId]);

  // Handle call timer
  useEffect(() => {
    if (isCallActive) {
      timerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setCallDuration(0);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isCallActive]);

  // Simulate call connection
  const handleStartCall = (lead) => {
    if (!lead) return;

    setSelectedLead(lead);
    setShowLeadSelector(false);

    // Simulate connecting to VoIP service
    setTimeout(() => {
      setIsCallActive(true);
      setCurrentCall({
        id: `call_${Date.now()}`,
        leadId: lead.id,
        leadName: lead.name,
        leadEmail: lead.email,
        leadPhone: lead.phone || '+33 6 XX XX XX XX',
        startedAt: new Date().toISOString(),
        endedAt: null,
        duration: 0,
        recording: false,
        transcript: [],
        notes: '',
      });

      // Simulate incoming voice activity
      simulateVoiceActivity();
    }, 1000);
  };

  // Simulate voice activity for demo
  const simulateVoiceActivity = () => {
    const voiceLines = [
      { speaker: 'lead', text: 'Bonjour, comment ça va?' },
      { speaker: 'user', text: 'Très bien, merci! Comment pouvons-nous collaborer?' },
      { speaker: 'lead', text: 'Nous sommes intéressés par votre solution...' },
      { speaker: 'user', text: 'Parfait! Laissez-moi vous présenter les avantages...' },
      { speaker: 'lead', text: 'Quand pouvez-vous nous faire une démonstration?' },
    ];

    let lineIndex = 0;
    const voiceInterval = setInterval(() => {
      if (lineIndex < voiceLines.length && isCallActive) {
        setCallTranscript(prev => [...prev, voiceLines[lineIndex]]);
        lineIndex++;
      } else if (lineIndex >= voiceLines.length) {
        clearInterval(voiceInterval);
      }
    }, 8000);
  };

  // Handle end call
  const handleEndCall = () => {
    if (!currentCall) return;

    const completedCall = {
      ...currentCall,
      endedAt: new Date().toISOString(),
      duration: callDuration,
      transcript: callTranscript,
    };

    setCallHistory([completedCall, ...callHistory]);
    setIsCallActive(false);
    setCurrentCall(null);
    setCallTranscript([]);
    setCallDuration(0);
  };

  // Format duration
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Start recording
  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      recordingRef.current = mediaRecorder;

      const audioChunks = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioUrl = window.URL.createObjectURL(audioBlob);
        const a = document.createElement('a');
        a.href = audioUrl;
        a.download = `call_${new Date().toISOString()}.webm`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(audioUrl);
        document.body.removeChild(a);
      };

      mediaRecorder.start();
      setCallRecording(true);
    } catch (err) {
      console.error('Microphone access denied:', err);
      alert('Accès au microphone refusé');
    }
  };

  // Stop recording
  const handleStopRecording = () => {
    if (recordingRef.current && recordingRef.current.state === 'recording') {
      recordingRef.current.stop();
      setCallRecording(false);
    }
  };

  return (
    <motion.div
      className="click-to-call"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      {isCallActive && currentCall ? (
        <div className="active-call">
          <motion.div
            className="call-window"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <div className="call-header">
              <div className="call-info">
                <h3>{currentCall.leadName}</h3>
                <p>{currentCall.leadPhone}</p>
              </div>
              <div className="call-duration">
                <Clock size={18} />
                <span>{formatDuration(callDuration)}</span>
              </div>
            </div>

            <div className="call-transcript">
              <div className="transcript-list">
                <AnimatePresence>
                  {callTranscript.map((line, idx) => (
                    <motion.div
                      key={idx}
                      className={`transcript-line ${line.speaker}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                    >
                      <span className="speaker-badge">{line.speaker === 'user' ? 'Vous' : 'Client'}</span>
                      <p>{line.text}</p>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            <div className="call-controls">
              <button
                className={`control-btn ${isMuted ? 'active' : ''}`}
                onClick={() => setIsMuted(!isMuted)}
                title="Couper le micro"
              >
                {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
              </button>

              <button
                className={`control-btn ${isSpeakerOn ? 'active' : ''}`}
                onClick={() => setIsSpeakerOn(!isSpeakerOn)}
                title="Haut-parleur"
              >
                {isSpeakerOn ? <Volume2 size={20} /> : <VolumeX size={20} />}
              </button>

              <button
                className={`control-btn ${callRecording ? 'recording' : ''}`}
                onClick={callRecording ? handleStopRecording : handleStartRecording}
                title={callRecording ? 'Arrêter l\'enregistrement' : 'Enregistrer'}
              >
                <div className={`record-dot ${callRecording ? 'active' : ''}`}></div>
                REC
              </button>

              <button
                className="control-btn skip"
                title="Message précédent"
              >
                <SkipBack size={20} />
              </button>

              <button
                className="control-btn skip"
                title="Message suivant"
              >
                <SkipForward size={20} />
              </button>

              <button
                className="end-call-btn"
                onClick={handleEndCall}
                title="Terminer l'appel"
              >
                <PhoneOff size={24} />
              </button>
            </div>
          </motion.div>
        </div>
      ) : (
        <div className="call-interface">
          <div className="interface-header">
            <h2>☎️ Click-to-Call VoIP</h2>
            <p>Appelez directement depuis votre CRM</p>
          </div>

          <AnimatePresence>
            {showLeadSelector ? (
              <motion.div
                className="lead-selector"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <div className="selector-content">
                  <h3>Sélectionner un contact</h3>
                  <div className="lead-options">
                    {leads.map(lead => (
                      <button
                        key={lead.id}
                        className="lead-option"
                        onClick={() => handleStartCall(lead)}
                      >
                        <div className="lead-info">
                          <p className="lead-name">{lead.name}</p>
                          <p className="lead-company">{lead.company}</p>
                          <p className="lead-phone">{lead.phone || '+33 6 XX XX XX XX'}</p>
                        </div>
                        <Phone size={20} />
                      </button>
                    ))}
                  </div>
                  <button
                    className="close-selector-btn"
                    onClick={() => setShowLeadSelector(false)}
                  >
                    Fermer
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.button
                className="start-call-btn"
                onClick={() => setShowLeadSelector(true)}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <Phone size={24} />
                Appeler un contact
              </motion.button>
            )}
          </AnimatePresence>

          <div className="call-history-section">
            <h3>Historique des appels</h3>
            <div className="history-list">
              {callHistory.length === 0 ? (
                <p className="empty-history">Aucun appel enregistré</p>
              ) : (
                callHistory.slice(0, 10).map(call => (
                  <motion.div
                    key={call.id}
                    className="history-item"
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <div className="history-lead">
                      <p className="history-name">{call.leadName}</p>
                      <p className="history-company">{call.leadEmail}</p>
                    </div>
                    <div className="history-meta">
                      <span className="history-date">
                        {new Date(call.startedAt).toLocaleDateString('fr-FR')}
                      </span>
                      <span className="history-duration">
                        {formatDuration(call.duration)}
                      </span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ClickToCall;
