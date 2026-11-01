import fs from 'fs/promises';
import path from 'path';
import { IStorageProvider } from './storage.interface.js';
import { ApiError } from '../../utils/apiError.js';
import { logger } from '../../utils/logger.js';

export class LocalStorageProvider extends IStorageProvider {
  /**
   * @param {string} rootDir - Root directory for local storage
   */
  constructor(rootDir) {
    super();
    this.rootDir = path.resolve(process.cwd(), rootDir);
  }

  /**
   * Resolve and sanitize a storage key into an absolute filesystem path.
   * Prevents path traversal vulnerabilities.
   *
   * @param {string} key
   * @returns {string}
   */
  #resolveSecurePath(key) {
    if (!key || typeof key !== 'string') {
      throw ApiError.badRequest('Invalid storage key');
    }
    const normalizedKey = path.normalize(key).replace(/^(\.\.(\/|\\|$))+/, '');
    const absolutePath = path.resolve(this.rootDir, normalizedKey);

    if (!absolutePath.startsWith(this.rootDir)) {
      throw ApiError.forbidden('Access denied: directory traversal attempt detected');
    }
    return absolutePath;
  }

  async putObject(key, buffer, contentType = 'application/octet-stream') {
    const targetPath = this.#resolveSecurePath(key);
    await fs.mkdir(path.dirname(targetPath), { recursive: true });
    await fs.writeFile(targetPath, buffer);

    logger.debug('Saved object to local storage', { key, sizeBytes: buffer.length });
    return {
      storageKey: key,
      sizeBytes: buffer.length
    };
  }

  async getObject(key) {
    const targetPath = this.#resolveSecurePath(key);
    try {
      return await fs.readFile(targetPath);
    } catch (err) {
      if (err.code === 'ENOENT') {
        throw ApiError.notFound(`Storage object not found: ${key}`);
      }
      throw err;
    }
  }

  async deleteObject(key) {
    const targetPath = this.#resolveSecurePath(key);
    try {
      await fs.unlink(targetPath);
      logger.debug('Deleted object from local storage', { key });
      return true;
    } catch (err) {
      if (err.code === 'ENOENT') {
        return false;
      }
      throw err;
    }
  }

  async exists(key) {
    const targetPath = this.#resolveSecurePath(key);
    try {
      await fs.access(targetPath);
      return true;
    } catch {
      return false;
    }
  }

  async getAbsolutePath(key) {
    return this.#resolveSecurePath(key);
  }
}

