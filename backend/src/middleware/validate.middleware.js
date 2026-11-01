import { ApiError } from '../utils/apiError.js';

/**
 * Middleware factory to validate request against a Zod schema
 * @param {import('zod').ZodSchema} schema
 * @param {'body'|'query'|'params'} [target='body']
 */
export function validate(schema, target = 'body') {
  return (req, res, next) => {
    const result = schema.safeParse(req[target]);
    if (!result.success) {
      const details = result.error.errors.map((err) => ({
        field: err.path.join('.'),
        issue: err.message
      }));
      return next(ApiError.badRequest('Request validation failed', details));
    }
    req[target] = result.data;
    next();
  };
}

