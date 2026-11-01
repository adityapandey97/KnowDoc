/**
 * Structured JSON Logger for KnowDoc Backend.
 * Automatically sanitizes sensitive keys and records correlation IDs.
 */

const SENSITIVE_KEYS = new Set([
  'password',
  'passwordhash',
  'token',
  'accesstoken',
  'refreshtoken',
  'authorization',
  'internalservicekey',
  'secret'
]);

function sanitize(obj, depth = 0) {
  if (depth > 4 || obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => sanitize(item, depth + 1));
  }

  const cleaned = {};
  for (const [key, value] of Object.entries(obj)) {
    if (SENSITIVE_KEYS.has(key.toLowerCase())) {
      cleaned[key] = '[REDACTED]';
    } else if (typeof value === 'object') {
      cleaned[key] = sanitize(value, depth + 1);
    } else {
      cleaned[key] = value;
    }
  }
  return cleaned;
}

function formatLog(level, message, meta = {}) {
  const entry = {
    timestamp: new Date().toISOString(),
    service: 'knowdoc-backend',
    level,
    message,
    ...sanitize(meta)
  };
  return JSON.stringify(entry);
}

export const logger = {
  info(message, meta) {
    console.log(formatLog('info', message, meta));
  },
  warn(message, meta) {
    console.warn(formatLog('warn', message, meta));
  },
  error(message, meta) {
    console.error(formatLog('error', message, meta));
  },
  debug(message, meta) {
    if (process.env.LOG_LEVEL === 'debug') {
      console.debug(formatLog('debug', message, meta));
    }
  }
};

