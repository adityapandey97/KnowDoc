import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { AiServiceClient } from '../src/integrations/ai/aiService.client.js';
import { validatePdfSignature } from '../src/utils/pdfValidator.js';

describe('Backend AI Integration and Validator Suite', () => {
  let client;
  let originalFetch;

  beforeEach(() => {
    client = new AiServiceClient();
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  test('AiServiceClient checkHealth calls /internal/v1/health with internal auth header', async () => {
    const mockHealthResponse = {
      status: 'healthy',
      service: 'knowdoc-ai-service',
      vector_dimension: 1536
    };

    let calledUrl = null;
    let calledOptions = null;

    global.fetch = async (url, options) => {
      calledUrl = url;
      calledOptions = options;
      return {
        ok: true,
        json: async () => mockHealthResponse
      };
    };

    const res = await client.checkHealth();
    assert.strictEqual(res.status, 'healthy');
    assert.strictEqual(res.vector_dimension, 1536);
    assert.ok(calledUrl.includes('/internal/v1/health'));
    assert.strictEqual(calledOptions.headers['X-Internal-Service-Key'], client.internalKey);
  });

  test('AiServiceClient indexDocument sends proper payload to /internal/v1/rag/index', async () => {
    const mockIngestResponse = {
      document_id: 'doc_node_123',
      status: 'ready',
      total_pages: 7,
      total_chunks: 18
    };

    let calledUrl = null;
    let requestBody = null;

    global.fetch = async (url, options) => {
      calledUrl = url;
      requestBody = JSON.parse(options.body);
      return {
        ok: true,
        json: async () => mockIngestResponse
      };
    };

    const result = await client.indexDocument({
      documentId: 'doc_node_123',
      userId: 'user_node_456',
      storagePath: '/data/storage/doc.pdf',
      chunkSize: 800,
      chunkOverlap: 150
    });

    assert.strictEqual(result.status, 'ready');
    assert.strictEqual(result.total_chunks, 18);
    assert.ok(calledUrl.includes('/internal/v1/rag/index'));
    assert.strictEqual(requestBody.document_id, 'doc_node_123');
    assert.strictEqual(requestBody.user_id, 'user_node_456');
  });

  test('AiServiceClient queryKnowledgeBase passes useAgent flag and query parameters', async () => {
    const mockChatResponse = {
      answer: 'Financial revenue for Q3 grew 18.5%.',
      citations: [
        {
          document_id: 'doc_fin',
          page_number: 2,
          chunk_id: 'chk_10',
          excerpt: '18.5% growth',
          similarity_score: 0.94
        }
      ],
      usage: { prompt_tokens: 150, completion_tokens: 30 },
      insufficient_evidence: false
    };

    let calledUrl = null;
    let requestBody = null;

    global.fetch = async (url, options) => {
      calledUrl = url;
      requestBody = JSON.parse(options.body);
      return {
        ok: true,
        json: async () => mockChatResponse
      };
    };

    const result = await client.queryKnowledgeBase({
      query: 'What was the Q3 revenue growth?',
      userId: 'user_fin',
      documentIds: ['doc_fin'],
      useAgent: true
    });

    assert.ok(result.answer.includes('18.5%'));
    assert.strictEqual(result.citations.length, 1);
    assert.strictEqual(result.citations[0].page_number, 2);
    assert.ok(calledUrl.includes('/internal/v1/chat'));
    assert.strictEqual(requestBody.use_agent, true);
  });

  test('validatePdfSignature accepts valid PDF and rejects non-PDF buffers', () => {
    const validPdfBuffer = Buffer.from('%PDF-1.7\n%âãÏÓ\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF');
    assert.doesNotThrow(() => validatePdfSignature(validPdfBuffer, 'application/pdf'));

    const fakePdfBuffer = Buffer.from('<html><body>Not a PDF</body></html>');
    assert.throws(() => validatePdfSignature(fakePdfBuffer, 'application/pdf'));
  });
});

