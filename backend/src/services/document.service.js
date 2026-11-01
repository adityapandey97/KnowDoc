import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import { documentRepository } from '../repositories/document.repository.js';
import { conversationRepository } from '../repositories/conversation.repository.js';
import { getStorageProvider } from '../integrations/storage/index.js';
import { enqueueDocumentIngestion } from '../integrations/queue/documentQueue.js';
import { validatePdfSignature } from '../utils/pdfValidator.js';
import { getPostgresPool } from '../config/postgres.js';
import { ApiError } from '../utils/apiError.js';
import { logger } from '../utils/logger.js';

export const documentService = {
  async uploadDocument({ userId, fileBuffer, originalFilename, mimeType }) {
    // 1. Validate PDF magic bytes and MIME type
    validatePdfSignature(fileBuffer, mimeType);

    // 2. Compute SHA-256 hash for deduplication
    const fileHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');

    // 3. Check for duplicates in user's library
    const existingDoc = await documentRepository.findDuplicate(userId, fileHash);
    if (existingDoc) {
      logger.info('Duplicate document upload detected', { userId, fileHash, existingId: existingDoc._id });
      return existingDoc;
    }

    // 4. Generate unique storage key
    const uniqueFileId = uuidv4();
    const storageKey = `uploads/documents/${userId}/${uniqueFileId}.pdf`;

    // 5. Store binary via storage provider abstraction
    const storage = getStorageProvider();
    await storage.putObject(storageKey, fileBuffer, 'application/pdf');

    // 6. Create document metadata record in MongoDB with 'pending' status
    const doc = await documentRepository.create({
      userId,
      filename: `${uniqueFileId}.pdf`,
      originalFilename,
      storageKey,
      fileHash,
      sizeBytes: fileBuffer.length,
      mimeType: 'application/pdf',
      status: 'pending'
    });

    // 7. Enqueue asynchronous ingestion job
    try {
      await enqueueDocumentIngestion({
        documentId: doc._id.toString(),
        userId: userId.toString(),
        storageKey,
        originalFilename
      });
    } catch (queueErr) {
      logger.warn('Failed to enqueue ingestion job; will remain in pending state', {
        error: queueErr.message,
        documentId: doc._id
      });
    }

    return doc;
  },

  async listDocuments(userId, query) {
    return documentRepository.findByUserId(userId, query);
  },

  async getDocumentById(userId, documentId) {
    const doc = await documentRepository.findByUserIdAndId(userId, documentId);
    if (!doc) {
      throw ApiError.notFound('Document not found');
    }
    return doc;
  },

  async deleteDocument(userId, documentId) {
    const doc = await documentRepository.findByUserIdAndId(userId, documentId);
    if (!doc) {
      throw ApiError.notFound('Document not found');
    }

    // 1. Delete vector chunks from PostgreSQL
    try {
      const pgPool = getPostgresPool();
      await pgPool.query(
        'DELETE FROM document_chunks WHERE user_id = $1 AND document_id = $2;',
        [userId.toString(), documentId.toString()]
      );
    } catch (pgErr) {
      logger.warn('Error purging vector chunks from PostgreSQL', { error: pgErr.message });
    }

    // 2. Delete raw file from storage provider
    try {
      const storage = getStorageProvider();
      await storage.deleteObject(doc.storageKey);
    } catch (storeErr) {
      logger.warn('Error deleting file from storage provider', { error: storeErr.message });
    }

    // 3. Remove document reference from conversations
    await conversationRepository.removeDocumentReference(documentId);

    // 4. Delete document record from MongoDB
    await documentRepository.deleteById(documentId);

    logger.info('Document deleted with cross-database cascade', { userId, documentId });
    return { id: documentId, deleted: true };
  }
};

