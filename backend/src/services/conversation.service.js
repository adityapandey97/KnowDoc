import { conversationRepository } from '../repositories/conversation.repository.js';
import { messageRepository } from '../repositories/message.repository.js';
import { documentRepository } from '../repositories/document.repository.js';
import { aiServiceClient } from '../integrations/ai/aiService.client.js';
import { ApiError } from '../utils/apiError.js';
import { logger } from '../utils/logger.js';

export const conversationService = {
  async createConversation(userId, { title, documentIds }) {
    // Verify user owns all referenced documents
    for (const docId of documentIds) {
      const doc = await documentRepository.findByUserIdAndId(userId, docId);
      if (!doc) {
        throw ApiError.badRequest(`Document ${docId} does not exist or does not belong to you.`);
      }
    }

    const conversation = await conversationRepository.create({
      userId,
      title: title || 'New Conversation',
      documentIds
    });

    return conversation;
  },

  async listConversations(userId, query) {
    return conversationRepository.findByUserId(userId, query);
  },

  async getConversationById(userId, conversationId) {
    const convo = await conversationRepository.findByUserIdAndId(userId, conversationId);
    if (!convo) {
      throw ApiError.notFound('Conversation not found');
    }
    const messages = await messageRepository.findByConversationId(conversationId);
    return {
      conversation: convo,
      messages
    };
  },

  async sendMessage(userId, conversationId, queryText) {
    // 1. Verify conversation ownership
    const convo = await conversationRepository.findByUserIdAndId(userId, conversationId);
    if (!convo) {
      throw ApiError.notFound('Conversation not found');
    }

    // 2. Persist user message
    const userMessage = await messageRepository.create({
      conversationId,
      userId,
      role: 'user',
      content: queryText
    });

    // 3. Fetch past messages for context
    const pastMessages = await messageRepository.findByConversationId(conversationId, { limit: 10 });
    const formattedHistory = pastMessages.map((m) => ({
      role: m.role,
      content: m.content
    }));

    // 4. Delegate to AI service for RAG
    const aiResponse = await aiServiceClient.queryKnowledgeBase({
      query: queryText,
      userId: userId.toString(),
      documentIds: convo.documentIds.map((id) => id.toString()),
      conversationHistory: formattedHistory
    });

    // 5. Persist assistant message with citations
    const assistantMessage = await messageRepository.create({
      conversationId,
      userId,
      role: 'assistant',
      content: aiResponse.answer,
      citations: (aiResponse.citations || []).map((c) => ({
        documentId: c.document_id,
        pageNumber: c.page_number,
        excerpt: c.excerpt,
        similarityScore: c.similarity_score
      })),
      tokenUsage: {
        promptTokens: aiResponse.prompt_tokens,
        completionTokens: aiResponse.completion_tokens,
        totalTokens: (aiResponse.prompt_tokens || 0) + (aiResponse.completion_tokens || 0)
      }
    });

    // 6. Update conversation last message timestamp
    await conversationRepository.updateLastMessage(conversationId);

    return {
      messageId: assistantMessage._id.toString(),
      role: 'assistant',
      content: assistantMessage.content,
      citations: assistantMessage.citations,
      tokenUsage: assistantMessage.tokenUsage,
      createdAt: assistantMessage.createdAt
    };
  }
};

