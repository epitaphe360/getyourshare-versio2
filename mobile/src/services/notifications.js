/**
 * notifications.js — Service de notifications push pour l'app mobile
 * Utilise @notifee/react-native pour les notifications locales
 * et Firebase Cloud Messaging (FCM) pour les notifications push distantes
 */

import {Platform} from 'react-native';

// Tentative d'import de notifee (optionnel — peut ne pas être installé)
let notifee = null;
try {
  notifee = require('@notifee/react-native').default;
} catch (_) {
  console.log('[Notifications] @notifee/react-native non disponible');
}

// ─── Canaux de notification (Android) ────────────────────────────────────────
const CHANNELS = {
  DEFAULT: {
    id: 'default',
    name: 'Général',
    importance: 4, // HIGH
  },
  LEADS: {
    id: 'leads',
    name: 'Nouveaux Leads',
    importance: 4,
    sound: 'default',
    vibration: true,
  },
  CONVERSIONS: {
    id: 'conversions',
    name: 'Conversions',
    importance: 4,
    sound: 'default',
  },
  MESSAGES: {
    id: 'messages',
    name: 'Messages',
    importance: 4,
    sound: 'default',
  },
  PAYMENTS: {
    id: 'payments',
    name: 'Paiements',
    importance: 4,
    sound: 'default',
  },
};

/**
 * Initialiser les canaux de notification (Android uniquement)
 */
export async function initNotificationChannels() {
  if (!notifee || Platform.OS !== 'android') return;
  try {
    for (const channel of Object.values(CHANNELS)) {
      await notifee.createChannel(channel);
    }
    console.log('[Notifications] Canaux initialisés');
  } catch (err) {
    console.error('[Notifications] Erreur init canaux:', err);
  }
}

/**
 * Demander la permission de notifications
 * @returns {Promise<boolean>} true si accordée
 */
export async function requestPermission() {
  if (!notifee) return false;
  try {
    const settings = await notifee.requestPermission();
    return settings.authorizationStatus >= 1;
  } catch (_) {
    return false;
  }
}

/**
 * Afficher une notification locale
 * @param {Object} opts
 * @param {string} opts.title
 * @param {string} opts.body
 * @param {'default'|'leads'|'conversions'|'messages'|'payments'} opts.channel
 * @param {Object} opts.data - données additionnelles
 */
export async function showLocalNotification({title, body, channel = 'default', data = {}}) {
  if (!notifee) {
    console.log(`[Notifications] ${title}: ${body}`);
    return;
  }
  try {
    await notifee.displayNotification({
      title,
      body,
      data,
      android: {
        channelId: channel,
        smallIcon: 'ic_notification',
        pressAction: {id: 'default'},
      },
      ios: {
        sound: 'default',
      },
    });
  } catch (err) {
    console.error('[Notifications] Erreur affichage:', err);
  }
}

// ─── Helpers métier ───────────────────────────────────────────────────────────

export function notifyNewLead(lead) {
  showLocalNotification({
    title: '🔥 Nouveau lead',
    body: `${lead.company_name || lead.contact_name} — ${lead.status}`,
    channel: 'leads',
    data: {type: 'lead', id: lead.id},
  });
}

export function notifyConversion(conversion) {
  showLocalNotification({
    title: '✅ Conversion validée !',
    body: `+${conversion.amount} MAD sur ${conversion.product_name}`,
    channel: 'conversions',
    data: {type: 'conversion', id: conversion.id},
  });
}

export function notifyNewMessage(message) {
  showLocalNotification({
    title: `💬 ${message.sender_name}`,
    body: message.content,
    channel: 'messages',
    data: {type: 'message', conversationId: message.conversation_id},
  });
}

export function notifyPayment(payout) {
  showLocalNotification({
    title: '💰 Paiement reçu',
    body: `${payout.amount} MAD ont été déposés sur votre compte.`,
    channel: 'payments',
    data: {type: 'payout', id: payout.id},
  });
}

export function notifyAffiliationApproved(request) {
  showLocalNotification({
    title: '🎉 Affiliation acceptée',
    body: `Vous pouvez maintenant promouvoir : ${request.product_name}`,
    channel: 'default',
    data: {type: 'affiliation', id: request.id},
  });
}

export default {
  init: initNotificationChannels,
  requestPermission,
  show: showLocalNotification,
  notifyNewLead,
  notifyConversion,
  notifyNewMessage,
  notifyPayment,
  notifyAffiliationApproved,
};
