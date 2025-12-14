/**
 * Service API pour les NOUVEAUX endpoints (v2.0)
 * AI, Advanced Analytics, Live Chat, Support, E-commerce, etc.
 */

import axios from 'axios';
import { API_URL } from '../config/api.config';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ============================================
// AI RECOMMENDATIONS
// ============================================

export const aiAPI = {
  getRecommendationsForYou: () => api.get('/ai/recommendations/for-you'),
  getCollaborativeRecommendations: () => api.get('/ai/recommendations/collaborative'),
  getContentBasedRecommendations: () => api.get('/ai/recommendations/content-based'),
  getHybridRecommendations: () => api.get('/ai/recommendations/hybrid'),
  getTrendingProducts: () => api.get('/ai/recommendations/trending'),
  getSimilarProducts: (productId) => api.get(`/ai/recommendations/similar/${productId}`),
  chatWithBot: (message, sessionId) => api.post('/ai/chatbot', { message, session_id: sessionId }),
  getChatbotHistory: (sessionId) => api.get('/ai/chatbot/history', { params: { session_id: sessionId } }),
  getInsights: () => api.get('/ai/insights'),
};

// ============================================
// ADVANCED ANALYTICS
// ============================================

export const advancedAnalyticsAPI = {
  getCohortAnalysis: (params) => api.get('/advanced-analytics/cohorts', { params }),
  getRFMAnalysis: () => api.get('/advanced-analytics/rfm-analysis'),
  getCustomerSegments: () => api.get('/advanced-analytics/segments'),
  createABTest: (testData) => api.post('/advanced-analytics/ab-tests', testData),
  getABTests: (status) => api.get('/advanced-analytics/ab-tests', { params: { status } }),
  getABTestResults: (testId) => api.get(`/advanced-analytics/ab-tests/${testId}/results`),
  assignUserToVariant: (testId, userId, variantId) =>
    api.post(`/advanced-analytics/ab-tests/${testId}/assign`, { test_id: testId, user_id: userId, variant_id: variantId }),
  stopABTest: (testId) => api.post(`/advanced-analytics/ab-tests/${testId}/stop`),
};

// ============================================
// CUSTOMER SUPPORT
// ============================================

export const supportAPI = {
  createTicket: (ticketData) => api.post('/support/tickets', ticketData),
  getTickets: (params) => api.get('/support/tickets', { params }),
  getTicket: (ticketId) => api.get(`/support/tickets/${ticketId}`),
  replyToTicket: (ticketId, message, isInternal = false) =>
    api.post(`/support/tickets/${ticketId}/reply`, { message, is_internal: isInternal }),
  updateTicketStatus: (ticketId, status) => api.put(`/support/tickets/${ticketId}/status`, { status }),
  updateTicketPriority: (ticketId, priority) => api.put(`/support/tickets/${ticketId}/priority`, { priority }),
  assignTicket: (ticketId, agentId) => api.post(`/support/tickets/${ticketId}/assign`, { agent_id: agentId }),
  closeTicket: (ticketId) => api.post(`/support/tickets/${ticketId}/close`),
  getTicketReplies: (ticketId) => api.get(`/support/tickets/${ticketId}/replies`),
  getSupportStats: () => api.get('/support/stats'),
  getCategories: () => api.get('/support/categories'),
};

// ============================================
// LIVE CHAT
// ============================================

export const liveChatAPI = {
  createRoom: (roomData) => api.post('/live-chat/rooms', roomData),
  getRooms: () => api.get('/live-chat/rooms'),
  getRoomHistory: (roomId, limit = 50) => api.get(`/live-chat/rooms/${roomId}/history`, { params: { limit } }),
  getRoomParticipants: (roomId) => api.get(`/live-chat/rooms/${roomId}/participants`),
  markAsRead: (roomId) => api.post(`/live-chat/rooms/${roomId}/mark-read`),

  getWebSocketURL: (userId) => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const backendURL = process.env.REACT_APP_BACKEND_URL || window.location.origin;
    const wsURL = backendURL.replace('https:', wsProtocol).replace('http:', wsProtocol);
    return `${wsURL}/api/live-chat/ws/${userId}`;
  },
};

// ============================================
// E-COMMERCE INTEGRATIONS
// ============================================

export const ecommerceAPI = {
  connectShopify: (shopUrl, accessToken) =>
    api.post('/ecommerce/shopify/connect', { shop_url: shopUrl, access_token: accessToken }),
  syncShopifyProducts: () => api.post('/ecommerce/shopify/sync-products'),

  connectWooCommerce: (shopUrl, consumerKey, consumerSecret) =>
    api.post('/ecommerce/woocommerce/connect', {
      shop_url: shopUrl,
      consumer_key: consumerKey,
      consumer_secret: consumerSecret
    }),
  syncWooCommerceProducts: () => api.post('/ecommerce/woocommerce/sync-products'),

  connectPrestaShop: (shopUrl, apiKey) =>
    api.post('/ecommerce/prestashop/connect', { shop_url: shopUrl, api_key: apiKey }),

  getConnectedStores: () => api.get('/ecommerce/connected'),
  disconnectPlatform: (platform) => api.post(`/ecommerce/${platform}/disconnect`),
};

// ============================================
// PAYMENT GATEWAYS
// ============================================

export const paymentAPI = {
  createStripeCheckout: (paymentData) => api.post('/payments/stripe/create-checkout', paymentData),
  verifyStripePayment: (sessionId) => api.post('/payments/stripe/verify-payment', { session_id: sessionId }),

  createPayPalOrder: (amount, currency = 'USD') =>
    api.post('/payments/paypal/create-order', { amount, currency }),
  executePayPalPayment: (orderId) => api.post('/payments/paypal/execute-payment', { order_id: orderId }),

  createCryptoPayment: (paymentData) => api.post('/payments/crypto/create-payment', paymentData),
  getCryptoPaymentStatus: (paymentId) => api.get(`/payments/crypto/status/${paymentId}`),

  getTransactions: (params) => api.get('/payments/transactions', { params }),
  getTransaction: (transactionId) => api.get(`/payments/transactions/${transactionId}`),
};

// ============================================
// KYC VERIFICATION
// ============================================

export const kycAPI = {
  uploadDocuments: (formData) =>
    api.post('/kyc/upload-documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getStatus: () => api.get('/kyc/status'),
  verifyKYC: (verificationData) => api.post('/kyc/verify', verificationData),
  getPendingVerifications: () => api.get('/kyc/admin/pending'),
  approveKYC: (userId, notes) => api.post(`/kyc/admin/approve/${userId}`, { notes }),
  rejectKYC: (userId, reason) => api.post(`/kyc/admin/reject/${userId}`, { reason }),
};

// ============================================
// CAMPAIGNS (Complete)
// ============================================

export const campaignsAPI = {
  activateCampaign: (campaignId) => api.post(`/campaigns/${campaignId}/activate`),
  pauseCampaign: (campaignId) => api.post(`/campaigns/${campaignId}/pause`),
  getCampaignAnalytics: (campaignId) => api.get(`/campaigns/${campaignId}/analytics`),
  inviteInfluencers: (campaignId, influencerIds) =>
    api.post(`/campaigns/${campaignId}/invite-influencers`, { influencer_ids: influencerIds }),
};

// ============================================
// PRODUCTS (Complete)
// ============================================

export const productsAPI = {
  bulkUpload: (productsData) => api.post('/products/bulk-upload', { products: productsData }),
  importCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/products/import-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  exportProducts: (params) => api.get('/products/export', { params, responseType: 'blob' }),
  duplicateProduct: (productId) => api.post(`/products/${productId}/duplicate`),
  getProductVariations: (productId) => api.get(`/products/${productId}/variations`),
  searchProducts: (query, filters) => api.get('/products/search', { params: { q: query, ...filters } }),
  getCategories: () => api.get('/products/categories'),
};

// ============================================
// CONTENT STUDIO (Complete)
// ============================================

export const contentStudioAPI = {
  generateCaption: (context) => api.post('/content-studio/generate-caption', { context }),
  generateHashtags: (content, category) =>
    api.post('/content-studio/generate-hashtags', { content, category }),
  schedulePost: (postData) => api.post('/content-studio/schedule-post', postData),
  getScheduledPosts: () => api.get('/content-studio/scheduled-posts'),
  deleteScheduledPost: (postId) => api.delete(`/content-studio/scheduled-posts/${postId}`),
  uploadMedia: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/content-studio/upload-media', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getMediaLibrary: (params) => api.get('/content-studio/media-library', { params }),
  createTemplate: (templateData) => api.post('/content-studio/create-template', templateData),
};

// ============================================
// MOBILE FEATURES
// ============================================

export const mobileAPI = {
  sendWhatsAppMessage: (toNumber, message) =>
    api.post('/whatsapp/send', { to_number: toNumber, message }),
  getWhatsAppMessages: (params) => api.get('/whatsapp/messages', { params }),

  createOrangeMoneyPayment: (phoneNumber, amount) =>
    api.post('/mobile-payments-ma/orange-money', { phone_number: phoneNumber, amount }),
  createInwiMoneyPayment: (phoneNumber, amount) =>
    api.post('/mobile-payments-ma/inwi-money', { phone_number: phoneNumber, amount }),
  createMarocTelecomPayment: (phoneNumber, amount) =>
    api.post('/mobile-payments-ma/maroc-telecom', { phone_number: phoneNumber, amount }),
  getMobilePaymentTransactions: (params) => api.get('/mobile-payments-ma/transactions', { params }),
};

export default {
  aiAPI,
  advancedAnalyticsAPI,
  supportAPI,
  liveChatAPI,
  ecommerceAPI,
  paymentAPI,
  kycAPI,
  campaignsAPI,
  productsAPI,
  contentStudioAPI,
  mobileAPI,
};
