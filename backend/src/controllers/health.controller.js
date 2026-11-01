import { isMongoHealthy } from '../config/database.js';
import { isRedisHealthy } from '../config/redis.js';

export const healthController = {
  async getHealth(req, res) {
    const mongoOk = isMongoHealthy();
    const redisOk = await isRedisHealthy();

    const isHealthy = mongoOk && redisOk;

    res.status(isHealthy ? 200 : 503).json({
      status: isHealthy ? 'healthy' : 'degraded',
      service: 'knowdoc-backend',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      uptimeSeconds: process.uptime(),
      dependencies: {
        mongodb: { status: mongoOk ? 'connected' : 'disconnected' },
        redis: { status: redisOk ? 'connected' : 'disconnected' }
      }
    });
  }
};

