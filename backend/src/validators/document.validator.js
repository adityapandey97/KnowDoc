import { z } from 'zod';

export const listDocumentsSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  status: z.enum(['pending', 'processing', 'chunked', 'embedding', 'ready', 'failed']).optional()
});

export const documentIdParamSchema = z.object({
  id: z.string().length(24, 'Document ID must be a 24-character hexadecimal ObjectId')
});

