import mongoose from 'mongoose';

const messageSchema = new mongoose.Schema(
  {
    conversationId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Conversation',
      required: true,
      index: true
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    role: {
      type: String,
      enum: ['user', 'assistant', 'system'],
      required: true
    },
    content: {
      type: String,
      required: true
    },
    citations: [
      {
        documentId: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'Document',
          required: true
        },
        documentName: { type: String },
        pageNumber: { type: Number, required: true },
        excerpt: { type: String, required: true },
        similarityScore: { type: Number }
      }
    ],
    tokenUsage: {
      promptTokens: { type: Number },
      completionTokens: { type: Number },
      totalTokens: { type: Number }
    }
  },
  {
    timestamps: true
  }
);

messageSchema.index({ conversationId: 1, createdAt: 1 });

export const Message = mongoose.model('Message', messageSchema);

