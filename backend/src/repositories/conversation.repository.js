import { Conversation } from '../models/conversation.model.js';

export const conversationRepository = {
  async findById(id) {
    return Conversation.findById(id).exec();
  },

  async findByUserIdAndId(userId, id) {
    return Conversation.findOne({ _id: id, userId }).exec();
  },

  async findByUserId(userId, { page = 1, limit = 20 } = {}) {
    const skip = (page - 1) * limit;
    const [data, total] = await Promise.all([
      Conversation.find({ userId }).sort({ lastMessageAt: -1 }).skip(skip).limit(limit).exec(),
      Conversation.countDocuments({ userId }).exec()
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    };
  },

  async create(convoData) {
    const convo = new Conversation(convoData);
    return convo.save();
  },

  async updateLastMessage(id) {
    return Conversation.findByIdAndUpdate(id, { lastMessageAt: new Date() }, { new: true }).exec();
  },

  async removeDocumentReference(documentId) {
    return Conversation.updateMany(
      { documentIds: documentId },
      { $pull: { documentIds: documentId } }
    ).exec();
  },

  async deleteById(id) {
    return Conversation.findByIdAndDelete(id).exec();
  }
};

