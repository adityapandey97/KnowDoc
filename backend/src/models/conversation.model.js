import mongoose from 'mongoose';

const conversationSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    title: {
      type: String,
      required: true,
      default: 'New Conversation'
    },
    documentIds: [
      {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Document',
        required: true
      }
    ],
    lastMessageAt: {
      type: Date,
      default: Date.now
    }
  },
  {
    timestamps: true
  }
);

conversationSchema.index({ userId: 1, lastMessageAt: -1 });

export const Conversation = mongoose.model('Conversation', conversationSchema);

