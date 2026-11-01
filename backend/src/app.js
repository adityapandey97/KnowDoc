import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config/env.js';
import apiRouter from './routes/index.js';
import { rateLimiter } from './middleware/rateLimiter.middleware.js';
import { errorHandler } from './middleware/error.middleware.js';
import { ApiError } from './utils/apiError.js';

export function createApp() {
  const app = express();

  // 1. Security Headers
  app.use(helmet());

  // 2. CORS
  app.use(
    cors({
      origin: config.corsOrigin,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Correlation-ID']
    })
  );

  // 3. Correlation ID injection
  app.use((req, res, next) => {
    const correlationId = req.headers['x-correlation-id'] || uuidv4();
    req.headers['x-correlation-id'] = correlationId;
    res.setHeader('X-Correlation-ID', correlationId);
    next();
  });

  // 4. Request Logging
  if (config.env !== 'test') {
    app.use(
      morgan(':method :url :status :res[content-length] - :response-time ms', {
        skip: (req) => req.url.includes('/health')
      })
    );
  }

  // 5. Rate limiting
  app.use(rateLimiter);

  // 6. JSON and URL-encoded body parsing
  app.use(express.json({ limit: '1mb' }));
  app.use(express.urlencoded({ extended: true, limit: '1mb' }));

  // 7. Mount Versioned API Routes
  app.use(config.apiPrefix, apiRouter);

  // 8. 404 Catch-all handler
  app.use((req, res, next) => {
    next(ApiError.notFound(`Endpoint not found: ${req.method} ${req.originalUrl}`));
  });

  // 9. Centralized Error Handler
  app.use(errorHandler);

  return app;
}

