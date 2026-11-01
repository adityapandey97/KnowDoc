import { z } from 'zod';

export const createConversationSchema = z.object({
  title: z.string().min(1).max(200).optional().default('New Conversation'),
  documentIds: z.array(z.string().length(24, 'Each documentId must be a valid 24-character ObjectId')).min(1, 'At least one document ID is required')
});

export const sendMessageSchema = z.object({
  query: z.string().min(1, 'Query cannot be empty').max(4000, 'Query exceeds 4000 character limit')
});

export const conversationIdParamSchema = z.object({
  id: z.string().length(24, 'Conversation ID must be a 24-character hexadecimal ObjectId')
});

