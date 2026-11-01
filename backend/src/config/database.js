import mongoose from 'mongoose';
import { config } from './env.js';
import { logger } from '../utils/logger.js';

let isConnected = false;

export async function connectMongo() {
  if (isConnected) return;

  try {
    mongoose.set('strictQuery', true);
    await mongoose.connect(config.mongodb.uri, {
      serverSelectionTimeoutMS: 5000,
      autoIndex: config.env !== 'production'
    });

    isConnected = true;
    logger.info('Connected to MongoDB', { uri: config.mongodb.uri.replace(/\/\/.*@/, '//***@') });
  } catch (error) {
    logger.error('Failed to connect to MongoDB', { error: error.message });
    throw error;
  }
}

export async function disconnectMongo() {
  if (!isConnected) return;
  await mongoose.disconnect();
  isConnected = false;
  logger.info('Disconnected from MongoDB');
}

export function isMongoHealthy() {
  return mongoose.connection.readyState === 1;
}

