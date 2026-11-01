import { jest } from '@jest/globals';
import { AiServiceClient } from '../src/integrations/ai/aiService.client.js';

describe('AiServiceClient Integration Tests', () => {
  let client;
  let originalFetch;

  beforeEach(() => {
    client = new AiServiceClient();
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('should call /internal/v1/health with internal auth header', async () => {
    const mockHealthResponse = {
      status: 'healthy',
      service: 'knowdoc-ai-service',
      vector_dimension: 1536
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealthResponse
    });

    const res = await client.checkHealth();
    expect(res.status).toBe('healthy');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/internal/v1/health'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-Internal-Service-Key': expect.any(String),
          'Content-Type': 'application/json'
        })
      })
    );
  });

  it('should post ingestion request to /internal/v1/rag/index', async () => {
    const mockIngestResponse = {
      document_id: 'doc_123',
      status: 'ready',
      total_pages: 5,
      total_chunks: 12
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockIngestResponse
    });

    const result = await client.indexDocument({
      documentId: 'doc_123',
      userId: 'user_456',
      storagePath: '/data/storage/doc_123.pdf'
    });

    expect(result.status).toBe('ready');
    expect(result.total_chunks).toBe(12);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/internal/v1/rag/index'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          document_id: 'doc_123',
          user_id: 'user_456',
          storage_path: '/data/storage/doc_123.pdf',
          chunk_size: 800,
          chunk_overlap: 150
        })
      })
    );
  });

  it('should query AI knowledge base with grounded citations', async () => {
    const mockChatResponse = {
      answer: 'Operating margin grew to 24.8%.',
      citations: [
        {
          document_id: 'doc_123',
          page_number: 4,
          chunk_id: 'chk_1',
          excerpt: '24.8%',
          similarity_score: 0.91
        }
      ],
      usage: { prompt_tokens: 120, completion_tokens: 25 },
      insufficient_evidence: false
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockChatResponse
    });

    const result = await client.queryKnowledgeBase({
      query: 'What was the operating margin?',
      userId: 'user_456',
      documentIds: ['doc_123'],
      useAgent: false
    });

    expect(result.answer).toContain('24.8%');
    expect(result.citations).toHaveLength(1);
    expect(result.citations[0].page_number).toBe(4);
  });
});

