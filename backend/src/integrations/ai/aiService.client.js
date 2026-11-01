import { config } from '../../config/env.js';
import { ApiError } from '../../utils/apiError.js';
import { logger } from '../../utils/logger.js';

export class AiServiceClient {
  constructor() {
    this.baseUrl = config.aiService.url;
    this.timeoutMs = config.aiService.timeoutMs;
    this.internalKey = config.internalServiceKey;
  }

  async #request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-Internal-Service-Key': this.internalKey,
      ...(options.headers || {})
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        logger.error('AI service request failed', {
          url,
          status: response.status,
          errorBody
        });
        throw new ApiError(
          response.status === 404 ? 404 : 502,
          errorBody.detail || 'Error communicating with internal AI service',
          'AI_SERVICE_ERROR'
        );
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeout);
      if (err.name === 'AbortError') {
        logger.error('AI service request timed out', { url, timeoutMs: this.timeoutMs });
        throw ApiError.serviceUnavailable('AI service request timed out');
      }
      if (err instanceof ApiError) throw err;

      logger.error('AI service connection error', { url, error: err.message });
      throw ApiError.serviceUnavailable('Failed to connect to internal AI service');
    }
  }

  async checkHealth() {
    return this.#request('/internal/v1/health', { method: 'GET' });
  }

  async indexDocument({ documentId, userId, storagePath, chunkSize = 800, chunkOverlap = 150 }) {
    return this.#request('/internal/v1/rag/index', {
      method: 'POST',
      body: JSON.stringify({
        document_id: documentId,
        user_id: userId,
        storage_path: storagePath,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap
      })
    });
  }

  async queryKnowledgeBase({ query, userId, documentIds, topK = 5, conversationHistory = [] }) {
    return this.#request('/internal/v1/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        user_id: userId,
        document_ids: documentIds,
        top_k: topK,
        conversation_history: conversationHistory
      })
    });
  }
}

export const aiServiceClient = new AiServiceClient();

