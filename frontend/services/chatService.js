import { apiClient } from './apiClient.js';

export const chatService = {
  async listConversations(params = {}) {
    return apiClient.get('/conversations', params);
  },

  async createConversation(title, documentIds) {
    return apiClient.post('/conversations', { title, documentIds });
  },

  async getConversation(id) {
    return apiClient.get(`/conversations/${id}`);
  },

  async sendMessage(conversationId, query, useAgent = false) {
    return apiClient.post(`/conversations/${conversationId}/messages`, { query, useAgent });
  }
};

