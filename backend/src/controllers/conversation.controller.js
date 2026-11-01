import { conversationService } from '../services/conversation.service.js';

export const conversationController = {
  async create(req, res, next) {
    try {
      const result = await conversationService.createConversation(req.user.id, req.body);
      res.status(201).json({
        success: true,
        data: {
          id: result._id.toString(),
          title: result.title,
          documentIds: result.documentIds,
          createdAt: result.createdAt
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async list(req, res, next) {
    try {
      const result = await conversationService.listConversations(req.user.id, req.query);
      res.status(200).json({
        success: true,
        data: result.data.map((c) => ({
          id: c._id.toString(),
          title: c.title,
          documentIds: c.documentIds,
          lastMessageAt: c.lastMessageAt,
          createdAt: c.createdAt
        })),
        pagination: {
          page: result.page,
          limit: result.limit,
          total: result.total,
          totalPages: result.totalPages,
          hasMore: result.page < result.totalPages
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async getById(req, res, next) {
    try {
      const result = await conversationService.getConversationById(req.user.id, req.params.id);
      res.status(200).json({
        success: true,
        data: {
          id: result.conversation._id.toString(),
          title: result.conversation.title,
          documentIds: result.conversation.documentIds,
          messages: result.messages.map((m) => ({
            id: m._id.toString(),
            role: m.role,
            content: m.content,
            citations: m.citations,
            createdAt: m.createdAt
          })),
          createdAt: result.conversation.createdAt
        }
      });
    } catch (err) {
      next(err);
    }
  },

  async sendMessage(req, res, next) {
    try {
      const message = await conversationService.sendMessage(
        req.user.id,
        req.params.id,
        req.body.query,
        Boolean(req.body.useAgent)
      );
      res.status(200).json({
        success: true,
        data: message
      });
    } catch (err) {
      next(err);
    }
  }
};

