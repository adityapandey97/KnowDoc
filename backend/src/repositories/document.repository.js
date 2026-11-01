import { Document } from '../models/document.model.js';

export const documentRepository = {
  async findById(id) {
    return Document.findById(id).exec();
  },

  async findByUserIdAndId(userId, id) {
    return Document.findOne({ _id: id, userId }).exec();
  },

  async findByUserId(userId, { page = 1, limit = 20, status } = {}) {
    const query = { userId };
    if (status) query.status = status;

    const skip = (page - 1) * limit;
    const [data, total] = await Promise.all([
      Document.find(query).sort({ createdAt: -1 }).skip(skip).limit(limit).exec(),
      Document.countDocuments(query).exec()
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    };
  },

  async findDuplicate(userId, fileHash) {
    return Document.findOne({ userId, fileHash }).exec();
  },

  async create(docData) {
    const doc = new Document(docData);
    return doc.save();
  },

  async updateStatus(id, status, extra = {}) {
    return Document.findByIdAndUpdate(id, { status, ...extra }, { new: true }).exec();
  },

  async deleteById(id) {
    return Document.findByIdAndDelete(id).exec();
  }
};

