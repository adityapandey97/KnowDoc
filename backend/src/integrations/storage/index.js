import { config } from '../../config/env.js';
import { LocalStorageProvider } from './localStorage.provider.js';

let storageInstance = null;

export function getStorageProvider() {
  if (!storageInstance) {
    if (config.storage.driver === 'local') {
      storageInstance = new LocalStorageProvider(config.storage.localRoot);
    } else {
      throw new Error(`Unsupported storage driver: ${config.storage.driver}`);
    }
  }
  return storageInstance;
}

