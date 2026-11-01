import { Worker } from 'bullmq';
import { INGESTION_QUEUE_NAME } from './documentQueue.js';
import { config } from '../../config/env.js';
import { documentRepository } from '../../repositories/document.repository.js';
import { aiServiceClient } from '../ai/aiService.client.js';
import { getStorageProvider } from '../storage/index.js';
import { logger } from '../../utils/logger.js';

let ingestionWorker = null;

export function initIngestionWorker() {
  if (ingestionWorker) return ingestionWorker;

  ingestionWorker = new Worker(
    INGESTION_QUEUE_NAME,
    async (job) => {
      const { documentId, userId, storageKey } = job.data;
      logger.info('Starting document ingestion worker job', {
        jobId: job.id,
        documentId,
        attempt: job.attemptsMade + 1
      });

      // 1. Update status to processing
      await documentRepository.updateStatus(documentId, 'processing');

      // 2. Resolve absolute file path from storage provider
      const storage = getStorageProvider();
      const absolutePath = await storage.getAbsolutePath(storageKey);

      // 3. Delegate to FastAPI AI service
      const indexResult = await aiServiceClient.indexDocument({
        documentId,
        userId,
        storagePath: absolutePath
      });

      // 4. Update status to ready
      await documentRepository.updateStatus(documentId, 'ready', {
        pageCount: indexResult.total_pages || 0,
        chunkCount: indexResult.total_chunks || 0
      });

      logger.info('Document ingestion successfully completed', {
        jobId: job.id,
        documentId,
        totalPages: indexResult.total_pages,
        totalChunks: indexResult.total_chunks
      });

      return indexResult;
    },
    {
      connection: {
        host: config.redis.host,
        port: config.redis.port,
        password: config.redis.password
      },
      concurrency: 5
    }
  );

  ingestionWorker.on('failed', async (job, err) => {
    logger.error('Ingestion worker job failed', {
      jobId: job?.id,
      documentId: job?.data?.documentId,
      error: err.message,
      attemptsMade: job?.attemptsMade
    });

    if (job && job.attemptsMade >= (job.opts.attempts || 3)) {
      // Retries exhausted -> mark as failed
      await documentRepository.updateStatus(job.data.documentId, 'failed', {
        errorDetails: {
          code: 'INGESTION_FAILED',
          message: err.message,
          failedAt: new Date()
        }
      });
    }
  });

  ingestionWorker.on('error', (err) => {
    logger.warn('Ingestion worker internal error', { error: err.message });
  });

  return ingestionWorker;
}

export async function stopIngestionWorker() {
  if (ingestionWorker) {
    await ingestionWorker.close();
    ingestionWorker = null;
    logger.info('Ingestion worker stopped');
  }
}

