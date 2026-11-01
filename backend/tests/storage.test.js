import path from 'path';
import fs from 'fs/promises';
import { LocalStorageProvider } from '../src/integrations/storage/localStorage.provider.js';
import { ApiError } from '../src/utils/apiError.js';

describe('LocalStorageProvider', () => {
  const testDir = 'data/test-storage';
  let storage;

  beforeAll(async () => {
    storage = new LocalStorageProvider(testDir);
  });

  afterAll(async () => {
    try {
      await fs.rm(path.resolve(process.cwd(), testDir), { recursive: true, force: true });
    } catch {
      // ignore
    }
  });

  it('should store and retrieve a file buffer', async () => {
    const key = 'docs/user-1/test.pdf';
    const content = Buffer.from('PDF test content');

    const result = await storage.putObject(key, content, 'application/pdf');
    expect(result.storageKey).toBe(key);
    expect(result.sizeBytes).toBe(content.length);

    const retrieved = await storage.getObject(key);
    expect(retrieved.toString()).toBe('PDF test content');

    const exists = await storage.exists(key);
    expect(exists).toBe(true);

    const deleted = await storage.deleteObject(key);
    expect(deleted).toBe(true);

    const existsAfter = await storage.exists(key);
    expect(existsAfter).toBe(false);
  });

  it('should reject path traversal attempts', async () => {
    const maliciousKey = '../../../../etc/passwd';
    await expect(storage.putObject(maliciousKey, Buffer.from('hack'))).rejects.toThrow(ApiError);
  });
});

