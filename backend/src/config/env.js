import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from project root if available
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

export const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '5000', 10),
  apiPrefix: process.env.API_PREFIX || '/api/v1',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:5173',

  jwt: {
    accessSecret: process.env.JWT_ACCESS_SECRET || 'dev-jwt-access-secret-minimum-32-characters-long',
    accessExpiresIn: process.env.JWT_ACCESS_EXPIRES_IN || '15m',
    refreshSecret: process.env.JWT_REFRESH_SECRET || 'dev-jwt-refresh-secret-minimum-32-characters-long',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d'
  },

  internalServiceKey: process.env.INTERNAL_SERVICE_KEY || 'dev-internal-secret-change-in-production',

  mongodb: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/knowdoc'
  },

  postgres: {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT || '5432', 10),
    database: process.env.POSTGRES_DB || 'knowdoc_vectors',
    user: process.env.POSTGRES_USER || 'knowdoc_vector_user',
    password: process.env.POSTGRES_PASSWORD || 'knowdoc_vector_password',
    maxConnections: parseInt(process.env.POSTGRES_MAX_CONNECTIONS || '20', 10),
    vectorDimension: parseInt(process.env.VECTOR_DIMENSION || '1536', 10)
  },

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined
  },

  storage: {
    driver: process.env.STORAGE_DRIVER || 'local',
    localRoot: process.env.STORAGE_LOCAL_ROOT || 'data/storage',
    maxFileSizeBytes: (parseInt(process.env.STORAGE_MAX_FILE_SIZE_MB || '25', 10)) * 1024 * 1024
  },

  aiService: {
    url: process.env.AI_SERVICE_URL || 'http://localhost:8000',
    timeoutMs: parseInt(process.env.AI_SERVICE_TIMEOUT_MS || '30000', 10)
  }
};

