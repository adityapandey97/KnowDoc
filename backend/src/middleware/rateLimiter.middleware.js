import { ApiError } from '../utils/apiError.js';

const requestCounts = new Map();
const WINDOW_MS = 60 * 1000; // 1 minute
const MAX_REQUESTS = 120; // 120 requests per minute

/**
 * Basic memory sliding window rate limiter for Phase 1
 */
export function rateLimiter(req, res, next) {
  const clientIp = req.ip || req.connection.remoteAddress || 'unknown';
  const now = Date.now();

  const record = requestCounts.get(clientIp) || { count: 0, resetTime: now + WINDOW_MS };

  if (now > record.resetTime) {
    record.count = 1;
    record.resetTime = now + WINDOW_MS;
  } else {
    record.count += 1;
  }

  requestCounts.set(clientIp, record);

  res.setHeader('X-RateLimit-Limit', MAX_REQUESTS);
  res.setHeader('X-RateLimit-Remaining', Math.max(0, MAX_REQUESTS - record.count));
  res.setHeader('X-RateLimit-Reset', Math.ceil(record.resetTime / 1000));

  if (record.count > MAX_REQUESTS) {
    return next(new ApiError(429, 'Too many requests. Please slow down.', 'RATE_LIMIT_EXCEEDED'));
  }

  next();
}

