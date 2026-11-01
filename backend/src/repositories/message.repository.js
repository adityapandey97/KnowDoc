import { Message } from '../models/message.model.js';

export const messageRepository = {
  async findByConversationId(conversationId, { limit = 50 } = {}) {
    return Message.find({ conversationId })
      .sort({ createdAt: 1 })
      .limit(limit)
      .exec();
  },

  async create(messageData) {
    const message = new Message(messageData);
    return message.save();
  },

  async deleteByConversationId(conversationId) {
    return Message.deleteMany({ conversationId }).exec();
  }
};

