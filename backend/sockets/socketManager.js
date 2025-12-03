const socketIO = require('socket.io');
const jwt = require('jsonwebtoken');

let io = null;

/**
 * Socket Manager - Gestion centralisée des WebSockets
 * Support: Notifications temps réel, Chat, Présence utilisateur
 */

/**
 * Initialiser Socket.IO
 */
function initializeSocket(server) {
  io = socketIO(server, {
    cors: {
      origin: process.env.FRONTEND_URL || 'http://localhost:3000',
      methods: ['GET', 'POST'],
      credentials: true
    },
    pingTimeout: 60000,
    pingInterval: 25000
  });

  // Middleware d'authentification
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token || socket.handshake.headers.authorization?.split(' ')[1];

      if (!token) {
        return next(new Error('Authentication error: No token provided'));
      }

      // Vérifier le token JWT
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      socket.userId = decoded.id;
      socket.userRole = decoded.role;

      console.log(`[Socket] User ${socket.userId} authenticated`);
      next();
    } catch (error) {
      console.error('[Socket] Authentication error:', error.message);
      next(new Error('Authentication error: Invalid token'));
    }
  });

  // Connexion
  io.on('connection', (socket) => {
    console.log(`[Socket] Client connected: ${socket.id} (User: ${socket.userId})`);

    // Joindre la room de l'utilisateur
    socket.join(`user_${socket.userId}`);

    // Émettre l'événement de connexion
    socket.emit('connected', {
      socket_id: socket.id,
      user_id: socket.userId
    });

    // Notifier le statut "online"
    io.emit('user:online', {
      user_id: socket.userId,
      timestamp: new Date()
    });

    // ========== NOTIFICATIONS ==========

    /**
     * Marquer une notification comme lue
     */
    socket.on('notification:mark-read', async (data) => {
      try {
        const { notification_id } = data;
        const NotificationService = require('../services/NotificationService');

        await NotificationService.markAsRead(notification_id, socket.userId);

        socket.emit('notification:marked-read', {
          notification_id,
          success: true
        });
      } catch (error) {
        console.error('[Socket] Error marking notification as read:', error);
        socket.emit('notification:error', {
          message: error.message
        });
      }
    });

    /**
     * Marquer toutes les notifications comme lues
     */
    socket.on('notification:mark-all-read', async () => {
      try {
        const NotificationService = require('../services/NotificationService');

        await NotificationService.markAllAsRead(socket.userId);

        socket.emit('notification:all-marked-read', {
          success: true
        });
      } catch (error) {
        console.error('[Socket] Error marking all notifications as read:', error);
        socket.emit('notification:error', {
          message: error.message
        });
      }
    });

    /**
     * Demander le nombre de notifications non lues
     */
    socket.on('notification:get-count', async () => {
      try {
        const Notification = require('../models/Notification');
        const unreadCount = await Notification.getUnreadCount(socket.userId);

        socket.emit('notification:count', unreadCount);
      } catch (error) {
        console.error('[Socket] Error getting notification count:', error);
        socket.emit('notification:error', {
          message: error.message
        });
      }
    });

    // ========== PRÉSENCE ==========

    /**
     * Mettre à jour le statut de présence
     */
    socket.on('presence:update', (data) => {
      const { status } = data; // 'online', 'away', 'busy', 'offline'

      // Émettre à tous les utilisateurs
      io.emit('user:status-change', {
        user_id: socket.userId,
        status,
        timestamp: new Date()
      });
    });

    /**
     * L'utilisateur est en train de taper (pour chat futur)
     */
    socket.on('typing:start', (data) => {
      const { room_id } = data;
      socket.to(room_id).emit('user:typing', {
        user_id: socket.userId,
        room_id
      });
    });

    socket.on('typing:stop', (data) => {
      const { room_id } = data;
      socket.to(room_id).emit('user:typing-stop', {
        user_id: socket.userId,
        room_id
      });
    });

    // ========== ROOMS (CHAT) ==========

    /**
     * Joindre une room de chat
     */
    socket.on('room:join', (data) => {
      const { room_id } = data;
      socket.join(room_id);

      console.log(`[Socket] User ${socket.userId} joined room ${room_id}`);

      socket.emit('room:joined', {
        room_id,
        timestamp: new Date()
      });

      // Notifier les autres membres de la room
      socket.to(room_id).emit('room:user-joined', {
        user_id: socket.userId,
        room_id,
        timestamp: new Date()
      });
    });

    /**
     * Quitter une room de chat
     */
    socket.on('room:leave', (data) => {
      const { room_id } = data;
      socket.leave(room_id);

      console.log(`[Socket] User ${socket.userId} left room ${room_id}`);

      socket.emit('room:left', {
        room_id,
        timestamp: new Date()
      });

      // Notifier les autres membres de la room
      socket.to(room_id).emit('room:user-left', {
        user_id: socket.userId,
        room_id,
        timestamp: new Date()
      });
    });

    // ========== DÉCONNEXION ==========

    socket.on('disconnect', (reason) => {
      console.log(`[Socket] Client disconnected: ${socket.id} (User: ${socket.userId}) - Reason: ${reason}`);

      // Notifier le statut "offline"
      io.emit('user:offline', {
        user_id: socket.userId,
        timestamp: new Date()
      });
    });

    // Gestion des erreurs
    socket.on('error', (error) => {
      console.error(`[Socket] Error on socket ${socket.id}:`, error);
    });
  });

  console.log('[Socket] Socket.IO initialized successfully');
  return io;
}

/**
 * Obtenir l'instance Socket.IO
 */
function getIO() {
  if (!io) {
    throw new Error('Socket.IO not initialized. Call initializeSocket first.');
  }
  return io;
}

/**
 * Émettre un événement à un utilisateur spécifique
 */
function emitToUser(userId, event, data) {
  if (!io) {
    console.error('[Socket] Socket.IO not initialized');
    return;
  }

  io.to(`user_${userId}`).emit(event, data);
}

/**
 * Émettre un événement à une room
 */
function emitToRoom(roomId, event, data) {
  if (!io) {
    console.error('[Socket] Socket.IO not initialized');
    return;
  }

  io.to(roomId).emit(event, data);
}

/**
 * Émettre un événement à tous les utilisateurs
 */
function emitToAll(event, data) {
  if (!io) {
    console.error('[Socket] Socket.IO not initialized');
    return;
  }

  io.emit(event, data);
}

/**
 * Obtenir le nombre de clients connectés
 */
async function getConnectedClientsCount() {
  if (!io) return 0;

  const sockets = await io.fetchSockets();
  return sockets.length;
}

/**
 * Obtenir les utilisateurs connectés dans une room
 */
async function getRoomMembers(roomId) {
  if (!io) return [];

  const sockets = await io.in(roomId).fetchSockets();
  return sockets.map(socket => socket.userId);
}

module.exports = {
  initializeSocket,
  getIO,
  emitToUser,
  emitToRoom,
  emitToAll,
  getConnectedClientsCount,
  getRoomMembers
};
