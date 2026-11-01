import request from 'supertest';
import { createApp } from '../src/app.js';

describe('Health API Endpoint', () => {
  let app;

  beforeAll(() => {
    app = createApp();
  });

  it('GET /api/v1/health should respond with service metadata', async () => {
    const res = await request(app).get('/api/v1/health');
    // In disconnected dev test mode it may return 200 or 503 depending on live DBs,
    // but the payload must be valid JSON with service name and status.
    expect(res.body).toHaveProperty('service', 'knowdoc-backend');
    expect(res.body).toHaveProperty('dependencies');
    expect(res.body.dependencies).toHaveProperty('mongodb');
    expect(res.body.dependencies).toHaveProperty('redis');
  });

  it('GET /api/v1/non-existent-route should respond with 404', async () => {
    const res = await request(app).get('/api/v1/non-existent-route');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('success', false);
    expect(res.body.error).toHaveProperty('code', 'NOT_FOUND');
  });
});

