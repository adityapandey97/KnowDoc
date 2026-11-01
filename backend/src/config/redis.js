import Redis from 'ioredis';
import { config } from './env.js';
import { logger } from '../utils/logger.js';

let redisClient = null;

export function getRedisClient() {
  if (!redisClient) {
    redisClient = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      maxRetriesPerRequest: null, // Required by BullMQ
      enableReadyCheck: false,
      lazyConnect: true
    });

    redisClient.on('connect', () => {
      logger.info('Connected to Redis', { host: config.redis.host, port: config.redis.port });
    });

    redisClient.on('error', (err) => {
      logger.warn('Redis connection warning', { error: err.message });
    });
  }
  return redisClient;
}

export async function disconnectRedis() {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
    logger.info('Disconnected from Redis');
  }
}

export async function isRedisHealthy() {
  try {
    const client = getRedisClient();
    if (client.status === 'ready' || client.status === 'connect') {
      const ping = await client.ping();
      return ping === 'PONG';
    }
    return false;
  } catch {
    return false;
  }
}

