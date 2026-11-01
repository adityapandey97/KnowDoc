import { ApiError } from './apiError.js';

/**
 * Standard PDF magic bytes: '%PDF-' (0x25 0x50 0x44 0x46 0x2D)
 */
const PDF_MAGIC_BYTES = Buffer.from([0x25, 0x50, 0x44, 0x46, 0x2D]);

/**
 * Validates that a file buffer represents a legitimate PDF document.
 * Inspects binary magic numbers rather than relying solely on file extensions.
 *
 * @param {Buffer} buffer - File buffer
 * @param {string} mimeType - Reported MIME type from multipart header
 * @returns {boolean}
 */
export function validatePdfSignature(buffer, mimeType) {
  if (!buffer || !Buffer.isBuffer(buffer)) {
    throw ApiError.unsupportedMediaType('Invalid or empty file payload.');
  }

  if (buffer.length < 5) {
    throw ApiError.unsupportedMediaType('File is corrupted or too small to be a valid PDF.');
  }

  // Verify reported MIME type
  if (mimeType && mimeType.toLowerCase() !== 'application/pdf') {
    throw ApiError.unsupportedMediaType(`Invalid MIME type: ${mimeType}. Only application/pdf is accepted.`);
  }

  // Check magic bytes within the first 1024 bytes (to accommodate optional BOM or headers)
  const headerSlice = buffer.subarray(0, Math.min(1024, buffer.length));
  const magicIndex = headerSlice.indexOf(PDF_MAGIC_BYTES);

  if (magicIndex === -1) {
    throw ApiError.unsupportedMediaType('File signature validation failed. Payload does not contain valid PDF magic bytes.');
  }

  return true;
}

