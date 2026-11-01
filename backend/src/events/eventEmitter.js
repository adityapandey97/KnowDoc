import { EventEmitter } from 'events';
import { logger } from '../utils/logger.js';

class AppEventEmitter extends EventEmitter {}

export const appEvents = new AppEventEmitter();

// Default error handler for event emitter to prevent process crashes
appEvents.on('error', (err) => {
  logger.error('Unhandled application event error', { error: err.message, stack: err.stack });
});

