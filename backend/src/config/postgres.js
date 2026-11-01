import pg from 'pg';
import { config } from './env.js';
import { logger } from '../utils/logger.js';

const { Pool } = pg;

let pool = null;

export function getPostgresPool() {
  if (!pool) {
    pool = new Pool({
      host: config.postgres.host,
      port: config.postgres.port,
      database: config.postgres.database,
      user: config.postgres.user,
      password: config.postgres.password,
      max: config.postgres.maxConnections,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000
    });

    pool.on('error', (err) => {
      logger.error('Unexpected error on idle PostgreSQL client', { error: err.message });
    });
  }
  return pool;
}

export async function disconnectPostgres() {
  if (pool) {
    await pool.end();
    pool = null;
    logger.info('Disconnected from PostgreSQL pool');
  }
}

export async function isPostgresHealthy() {
  try {
    const p = getPostgresPool();
    const res = await p.query('SELECT 1 AS healthy;');
    return res.rows[0]?.healthy === 1;
  } catch {
    return false;
  }
}

