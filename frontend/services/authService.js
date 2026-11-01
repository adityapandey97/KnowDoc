import { apiClient } from './apiClient.js';

export const authService = {
  async register(data) {
    const res = await apiClient.post('/auth/register', data);
    if (res.data?.tokens?.accessToken) {
      apiClient.setAuthToken(res.data.tokens.accessToken);
    }
    return res.data;
  },

  async login(credentials) {
    const res = await apiClient.post('/auth/login', credentials);
    if (res.data?.tokens?.accessToken) {
      apiClient.setAuthToken(res.data.tokens.accessToken);
    }
    return res.data;
  },

  async getProfile() {
    return apiClient.get('/auth/me');
  },

  logout() {
    apiClient.setAuthToken(null);
  }
};

