/**
 * Custom application API error with HTTP status codes and structured details.
 */
export class ApiError extends Error {
  /**
   * @param {number} statusCode - HTTP status code
   * @param {string} message - Human readable error message
   * @param {string} [code='INTERNAL_ERROR'] - Machine readable error code
   * @param {Array<Object>} [details=[]] - Optional validation or field error details
   */
  constructor(statusCode, message, code = 'INTERNAL_ERROR', details = []) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }

  static badRequest(message, details = []) {
    return new ApiError(400, message, 'VALIDATION_ERROR', details);
  }

  static unauthorized(message = 'Unauthorized') {
    return new ApiError(401, message, 'UNAUTHORIZED');
  }

  static forbidden(message = 'Forbidden') {
    return new ApiError(403, message, 'FORBIDDEN');
  }

  static notFound(message = 'Resource not found') {
    return new ApiError(404, message, 'NOT_FOUND');
  }

  static fileTooLarge(message = 'Uploaded file exceeds the maximum size limit') {
    return new ApiError(413, message, 'FILE_TOO_LARGE');
  }

  static unsupportedMediaType(message = 'Unsupported file format') {
    return new ApiError(415, message, 'INVALID_FILE_TYPE');
  }

  static internal(message = 'An unexpected internal error occurred') {
    return new ApiError(500, message, 'INTERNAL_ERROR');
  }

  static serviceUnavailable(message = 'Downstream service unavailable') {
    return new ApiError(503, message, 'SERVICE_UNAVAILABLE');
  }
}

