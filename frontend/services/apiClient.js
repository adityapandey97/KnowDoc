/**
 * Centralized API Client for KnowDoc Frontend.
 * Communicates exclusively with the Node.js/Express API Gateway.
 */

class ApiClient {
  constructor(baseUrl = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  getAuthToken() {
    return localStorage.getItem('knowdoc_access_token') || '';
  }

  setAuthToken(token) {
    if (token) {
      localStorage.setItem('knowdoc_access_token', token);
    } else {
      localStorage.removeItem('knowdoc_access_token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getAuthToken();

    const headers = {
      ...(options.isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const error = new Error(data?.error?.message || 'Network request failed');
        error.status = response.status;
        error.code = data?.error?.code || 'HTTP_ERROR';
        error.details = data?.error?.details || [];
        throw error;
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${url}:`, err);
      throw err;
    }
  }

  get(endpoint, queryParams = {}) {
    const search = new URLSearchParams(queryParams).toString();
    const url = search ? `${endpoint}?${search}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  postFormData(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      isFormData: true
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

