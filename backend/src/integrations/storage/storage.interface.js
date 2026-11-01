/**
 * Abstract interface for binary file storage.
 * Decouples application logic from filesystem or S3 object stores.
 */
export class IStorageProvider {
  /**
   * Put object into storage.
   * @param {string} key - Unique path/key identifier
   * @param {Buffer} buffer - File buffer
   * @param {string} contentType - MIME type
   * @returns {Promise<{ storageKey: string, sizeBytes: number }>}
   */
  async putObject(key, buffer, contentType) {
    throw new Error('IStorageProvider.putObject must be implemented by subclass');
  }

  /**
   * Retrieve binary buffer from storage.
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<Buffer>}
   */
  async getObject(key) {
    throw new Error('IStorageProvider.getObject must be implemented by subclass');
  }

  /**
   * Delete object permanently.
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<boolean>}
   */
  async deleteObject(key) {
    throw new Error('IStorageProvider.deleteObject must be implemented by subclass');
  }

  /**
   * Check if object exists.
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<boolean>}
   */
  async exists(key) {
    throw new Error('IStorageProvider.exists must be implemented by subclass');
  }

  /**
   * Resolve an absolute filesystem path or presigned access URL.
   * @param {string} key - Unique path/key identifier
   * @returns {Promise<string>}
   */
  async getAbsolutePath(key) {
    throw new Error('IStorageProvider.getAbsolutePath must be implemented by subclass');
  }
}

