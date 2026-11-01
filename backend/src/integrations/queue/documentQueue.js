import { Queue } from 'bullmq';
import { config } from '../../config/env.js';
import { logger } from '../../utils/logger.js';

export const INGESTION_QUEUE_NAME = 'knowdoc:queue:ingestion';

let ingestionQueue = null;

export function getDocumentQueue() {
  if (!ingestionQueue) {
    ingestionQueue = new Queue(INGESTION_QUEUE_NAME, {
      connection: {
        host: config.redis.host,
        port: config.redis.port,
        password: config.redis.password
      },
      defaultJobOptions: {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 5000
        },
        removeOnComplete: {
          age: 86400, // 24 hours
          count: 1000
        },
        removeOnFail: {
          age: 604800 // 7 days
        }
      }
    });

    ingestionQueue.on('error', (err) => {
      logger.warn('Document queue error', { error: err.message });
    });
  }
  return ingestionQueue;
}

export async function enqueueDocumentIngestion(payload) {
  const queue = getDocumentQueue();
  const job = await queue.add('process-document', payload, {
    jobId: `ingest_${payload.documentId}`
  });
  logger.info('Document ingestion job enqueued', {
    jobId: job.id,
    documentId: payload.documentId,
    userId: payload.userId
  });
  return job;
}

