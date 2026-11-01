import { createApp } from './app.js';
import { config } from './config/env.js';
import { connectMongo, disconnectMongo } from './config/database.js';
import { disconnectRedis } from './config/redis.js';
import { disconnectPostgres } from './config/postgres.js';
import { initIngestionWorker, stopIngestionWorker } from './integrations/queue/worker.js';
import { logger } from './utils/logger.js';

const app = createApp();

let server;

async function bootstrap() {
  try {
    logger.info('Initializing KnowDoc Backend services...');

    // Attempt database connections (non-fatal if services are starting up in dev)
    try {
      await connectMongo();
    } catch (dbErr) {
      logger.warn('Initial MongoDB connection failed; server will continue running', { error: dbErr.message });
    }

    // Initialize BullMQ background worker
    try {
      initIngestionWorker();
    } catch (queueErr) {
      logger.warn('Failed to start ingestion worker; background queue disabled', { error: queueErr.message });
    }

    server = app.listen(config.port, () => {
      logger.info(`KnowDoc API Gateway running at http://localhost:${config.port}${config.apiPrefix}`, {
        port: config.port,
        env: config.env
      });
    });
  } catch (err) {
    logger.error('Fatal bootstrap failure', { error: err.message, stack: err.stack });
    process.exit(1);
  }
}

async function gracefulShutdown(signal) {
  logger.info(`Received ${signal}. Initiating graceful shutdown...`);

  if (server) {
    server.close(() => {
      logger.info('HTTP server closed');
    });
  }

  try {
    await stopIngestionWorker();
    await disconnectMongo();
    await disconnectRedis();
    await disconnectPostgres();
    logger.info('All database connections cleanly terminated. Exiting.');
    process.exit(0);
  } catch (err) {
    logger.error('Error during graceful shutdown', { error: err.message });
    process.exit(1);
  }
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled Promise Rejection', { reason });
});

process.on('uncaughtException', (err) => {
  logger.error('Uncaught Exception', { error: err.message, stack: err.stack });
  process.exit(1);
});

bootstrap();

