import { apiClient } from './apiClient.js';

export const documentService = {
  async listDocuments(params = {}) {
    return apiClient.get('/documents', params);
  },

  async getDocument(id) {
    return apiClient.get(`/documents/${id}`);
  },

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.postFormData('/documents', formData);
  },

  async deleteDocument(id) {
    return apiClient.delete(`/documents/${id}`);
  }
};

