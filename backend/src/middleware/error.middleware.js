import { ApiError } from '../utils/apiError.js';
import { logger } from '../utils/logger.js';

export function errorHandler(err, req, res, next) {
  const correlationId = req.headers['x-correlation-id'] || 'system';

  let statusCode = 500;
  let code = 'INTERNAL_ERROR';
  let message = 'An unexpected internal server error occurred.';
  let details = [];

  if (err instanceof ApiError) {
    statusCode = err.statusCode;
    code = err.code;
    message = err.message;
    details = err.details || [];
  } else if (err.name === 'ValidationError') {
    // Mongoose validation error
    statusCode = 400;
    code = 'VALIDATION_ERROR';
    message = 'Validation failed';
    details = Object.values(err.errors || {}).map((e) => ({
      field: e.path,
      issue: e.message
    }));
  } else if (err.code === 11000) {
    // Mongo duplicate key
    statusCode = 409;
    code = 'CONFLICT';
    message = 'A resource with this identifier already exists.';
  } else if (err.name === 'MulterError') {
    statusCode = 400;
    code = 'UPLOAD_ERROR';
    message = err.message;
  }

  // Log server errors
  if (statusCode >= 500) {
    logger.error('Unhandled request exception', {
      correlationId,
      path: req.originalUrl,
      method: req.method,
      error: err.message,
      stack: process.env.NODE_ENV !== 'production' ? err.stack : undefined
    });
  } else {
    logger.warn('Client request error', {
      correlationId,
      path: req.originalUrl,
      method: req.method,
      statusCode,
      code,
      message
    });
  }

  res.status(statusCode).json({
    success: false,
    error: {
      code,
      message,
      correlationId,
      details
    }
  });
}

